#!/usr/bin/env python3
"""Check a local RAGFlow runtime with disposable TXT/DOCX/PDF full-text data."""
import argparse
import base64
import io
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
os.umask(0o077)


def encrypted(password):
    process = subprocess.run(
        ['openssl', 'pkeyutl', '-encrypt', '-pubin', '-inkey',
         str(ROOT / 'upstream/conf/public.pem'), '-pkeyopt', 'rsa_padding_mode:pkcs1'],
        input=base64.b64encode(password.encode()), capture_output=True, check=True)
    return base64.b64encode(process.stdout).decode()


def docx(text):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml',
                         '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                         '<Default Extension="xml" ContentType="application/xml"/>'
                         '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr('_rels/.rels',
                         '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr('word/document.xml',
                         '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                         '<w:body><w:p><w:r><w:t>' + text + '</w:t></w:r></w:p><w:sectPr/></w:body></w:document>')
    return buffer.getvalue()


def pdf(text):
    stream = ('BT /F1 12 Tf 50 740 Td (' + text + ') Tj ET').encode('ascii')
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>',
               b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
               b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream']
    data = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(str(index).encode() + b' 0 obj\n' + obj + b'\nendobj\n')
    start = len(data)
    data.extend(b'xref\n0 6\n0000000000 65535 f \n')
    for offset in offsets[1:]:
        data.extend(f'{offset:010} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode())
    return bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, choices=[18080, 18081], required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    env = dict(line.split('=', 1) for line in (ROOT / '.env').read_text().splitlines()
               if line and not line.startswith('#') and '=' in line)
    base = 'http://127.0.0.1:' + str(args.port)
    report = {'base': base, 'checks': [], 'documents': [], 'retrieval_mode': 'BM25/full-text; no embedding service required'}
    email = 'runtime-smoke-' + secrets.token_hex(6) + '@ragflow.local'
    password = secrets.token_urlsafe(24)
    marker = 'CobaltPinecone' + secrets.token_hex(5)
    report['synthetic_user'] = email
    admin = owner = dataset = None
    user_created = False

    def save():
        (args.output_dir / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    def request(label, path, body=None, token=None, method=None, content_type='application/json', require_success=True):
        headers = {'Content-Type': content_type}
        if token:
            headers['Authorization'] = token
        data = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
        started = time.monotonic()
        try:
            response = urllib.request.urlopen(req, timeout=45)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            try:
                result = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                result = raw
            status, response_headers = response.status, response.headers
        code = result.get('code') if isinstance(result, dict) else None
        report['checks'].append({'label': label, 'http': status, 'code': code,
                                 'duration_seconds': round(time.monotonic() - started, 3)})
        save()
        print(f'{label}: HTTP {status}, code {code}', flush=True)
        if require_success and (status != 200 or not isinstance(result, dict) or code != 0):
            message = result.get('message', '') if isinstance(result, dict) else ''
            raise RuntimeError(f'{label} failed: {str(message)[:350]}')
        return result.get('data') if isinstance(result, dict) else result, response_headers, result

    try:
        _, _, config = request('registration-disabled', '/api/v1/system/config')
        assert config['data']['registerEnabled'] is False
        _, _, health = request('health', '/api/v1/system/healthz', require_success=False)
        assert health['status'] == 'ok'
        _, _, blocked = request('MCP-blocked', '/api/v1/mcp', {}, require_success=False)
        assert report['checks'][-1]['http'] == 404
        _, headers, _ = request('admin-login', '/api/v1/admin/login', {
            'email': env['DEFAULT_SUPERUSER_EMAIL'], 'password': encrypted(env['ADMIN_DEFAULT_PASSWORD'])})
        admin = headers.get('Authorization')
        assert admin
        request('create-disposable-user', '/api/v1/admin/users', {
            'username': email, 'password': encrypted(password), 'role': 'user'}, admin)
        user_created = True
        _, headers, _ = request('ordinary-login', '/api/v1/auth/login', {
            'email': email, 'password': encrypted(password)})
        owner = headers.get('Authorization')
        assert owner
        info, _, _ = request('create-fulltext-dataset', '/api/v1/datasets', {
            'name': 'Runtime minimal smoke ' + marker, 'parse_type': 1, 'parser_id': 'general',
            'permission': 'me', 'language': 'English',
            'parser_config': {'Tokenizer:LegalReadersDecide': {'search_method': ['full_text'], 'fields': 'text'}}}, owner)
        dataset = info['id']
        assert not info.get('embedding_model'), 'Synthetic full-text dataset unexpectedly has an embedding model'
        text = f'The verification code is {marker}. This synthetic document checks native parsing and full text retrieval.'
        fixtures = {'sample.txt': text.encode(), 'sample.docx': docx(text), 'sample.pdf': pdf(text)}
        ids = []
        for name, content in fixtures.items():
            (args.output_dir / name).write_bytes(content)
            boundary = 'runtime-' + secrets.token_hex(10)
            payload = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\n'
                       'Content-Type: application/octet-stream\r\n\r\n').encode() + content + f'\r\n--{boundary}--\r\n'.encode()
            docs, _, _ = request('upload-' + name, f'/api/v1/datasets/{dataset}/documents', payload, owner,
                                 content_type='multipart/form-data; boundary=' + boundary)
            ids.append(docs[0]['id'])
        request('parse-native-documents', f'/api/v1/datasets/{dataset}/chunks', {'document_ids': ids}, owner)
        deadline = time.monotonic() + 240
        while True:
            data, _, _ = request('document-status', f'/api/v1/datasets/{dataset}/documents', token=owner)
            report['documents'] = [{'name': d['name'], 'id': d['id'], 'status': d.get('ingestion_status'),
                                    'chunks': d.get('chunk_count')} for d in data.get('docs', [])]
            save()
            if any(d['status'] in ('FAILED', 'FAIL', 'CANCELLED') for d in report['documents']):
                report['ingestion_errors'] = [d.get('latest_ingestion_event') for d in data.get('docs', [])]
                raise RuntimeError('Native document ingestion failed; inspect results.json')
            if len(report['documents']) == 3 and all(d['status'] == 'COMPLETED' and d['chunks'] > 0 for d in report['documents']):
                break
            if time.monotonic() >= deadline:
                raise TimeoutError('Native document ingestion timed out')
            time.sleep(3)
        result, _, _ = request('fulltext-retrieval', f'/api/v1/datasets/{dataset}/search', {
            'question': marker, 'vector_similarity_weight': 0.0, 'keywords_similarity_weight': 1.0,
            'similarity_threshold': 0.0, 'page_size': 10, 'keyword': False}, owner)
        chunks = result.get('chunks', [])
        found = {c.get('document_id', c.get('doc_id')) for c in chunks if marker in str(c)}
        assert set(ids).issubset(found), 'Retrieval did not return the marker from all three document formats'
        report['retrieval'] = {'chunks': len(chunks), 'all_formats_found': True}
        original, _, _ = request('download-original-docx', f'/api/v1/datasets/{dataset}/documents/{ids[1]}', token=owner,
                                 require_success=False)
        assert isinstance(original, bytes) and original == fixtures['sample.docx']
        report['passed'] = True
    except Exception as error:
        report['passed'] = False
        report['error'] = str(error)
        raise
    finally:
        cleanup = []
        if dataset and owner:
            try:
                request('cleanup-dataset', '/api/v1/datasets', {'ids': [dataset]}, owner, method='DELETE')
                cleanup.append('dataset-and-documents')
            except Exception as error:
                cleanup.append('dataset-cleanup-failed: ' + str(error))
        if user_created and admin:
            try:
                assert email.startswith('runtime-smoke-')
                request('deactivate-disposable-user', '/api/v1/admin/users/' + email + '/activate',
                        {'activate_status': 'off'}, admin, method='PUT')
                request('delete-disposable-user', '/api/v1/admin/users/' + email, token=admin, method='DELETE')
                cleanup.append('user')
            except Exception as error:
                cleanup.append('user-cleanup-failed: ' + str(error))
        report['cleanup'] = cleanup
        save()
    print(json.dumps({'passed': report.get('passed'), 'documents': report['documents'], 'retrieval': report.get('retrieval'),
                      'cleanup': report['cleanup']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
