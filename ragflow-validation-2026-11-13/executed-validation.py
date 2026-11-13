#!/usr/bin/env python3
"""Authorized F01/F02 HTTP validation against the existing local lab only.
Credentials stay in a mode-0600 temporary state file; evidence is redacted.
Usage: python3 validate_lab.py setup|ingest|f01|f02|cleanup|status
"""
import base64, datetime, hashlib, json, os, secrets, subprocess, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path
os.umask(0o077)
ROOT=Path('/Users/ruslan/recent-work/ragflow')
OUT=Path(__file__).resolve().parent
STATE=OUT/'private-state.json'
EVIDENCE=OUT/'evidence.json'
ENV=dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if line and not line.startswith('#') and '=' in line)
BASE='http://127.0.0.1:'+ENV['LAB_PORT']
S=json.loads(STATE.read_text()) if STATE.exists() else {}
E=json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else {'scope':str(ROOT),'date':'2026-11-13','events':[]}
def save():
    STATE.write_text(json.dumps(S,indent=2)); STATE.chmod(0o600)
    EVIDENCE.write_text(json.dumps(E,ensure_ascii=False,indent=2)+'\n')
def scrub(x):
    if isinstance(x,dict):
        return {k:('[REDACTED]' if any(z in k.lower() for z in ('password','token','beta','authorization','secret','api_key')) else scrub(v)) for k,v in x.items()}
    if isinstance(x,list): return [scrub(v) for v in x]
    if isinstance(x,str):
        for k,v in list(S.items())+list(ENV.items()):
            if isinstance(v,str) and len(v)>12 and any(z in k.lower() for z in ('password','token','beta','secret','key')):
                x=x.replace(v,'[REDACTED]')
        return x
    return x
def enc(p):
    r=subprocess.run(['openssl','pkeyutl','-encrypt','-pubin','-inkey',str(ROOT/'upstream/conf/public.pem'),'-pkeyopt','rsa_padding_mode:pkcs1'],input=base64.b64encode(p.encode()),capture_output=True,check=True)
    return base64.b64encode(r.stdout).decode()
def call(label,path,body=None,token=None,method=None,direct=False,content_type='application/json',headers=None):
    assert path.startswith('/api/v1/') and not path.startswith('//')
    h={'Content-Type':content_type,'Accept':'application/json, text/event-stream'}
    if token: h['Authorization']=token if token.startswith('Bearer ') else 'Bearer '+token
    h.update(headers or {})
    data=body if isinstance(body,bytes) else json.dumps(body).encode() if body is not None else None
    method=method or ('POST' if body is not None else 'GET')
    if direct:
        cfg=['silent','show-error','max-time = 45','dump-header = "-"','url = '+json.dumps('http://127.0.0.1:9380'+path),'request = '+json.dumps(method)]
        cfg += ['header = '+json.dumps(k+': '+v) for k,v in h.items()]
        if data is not None: cfg+=['data-binary = '+json.dumps(data.decode())]
        r=subprocess.run([str(ROOT/'lab.sh'),'compose','exec','-T','ragflow','curl','--config','-'],input=('\n'.join(cfg)+'\n').encode(),capture_output=True,timeout=55)
        if r.returncode: raise RuntimeError('Container curl failed '+str(r.returncode))
        raw=r.stdout
        head,sep,raw=raw.partition(b'\r\n\r\n')
        if not sep: raise RuntimeError('No HTTP headers from container curl')
        lines=head.decode().splitlines(); status=int(lines[0].split()[1]); rh=dict(line.split(': ',1) for line in lines[1:] if ': ' in line)
    else:
        req=urllib.request.Request(BASE+path,data=data,headers=h,method=method)
        try: resp=urllib.request.urlopen(req,timeout=45)
        except urllib.error.HTTPError as error: resp=error
        with resp:
            status=resp.status; rh=dict(resp.headers); raw=resp.read()
    try: result=json.loads(raw)
    except (ValueError,UnicodeDecodeError): result=raw.decode(errors='replace')
    ev={'label':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'via':'container loopback :9380 (diagnostic, gateway bypassed)' if direct else 'lab nginx 127.0.0.1:'+ENV['LAB_PORT'],'method':method,'path':scrub(path),'credential_class':label.split(':')[0],'status':status,'response':scrub(result)}
    if data is not None and not isinstance(body,bytes): ev['request']=scrub(body)
    E['events'].append(ev); save()
    print(label,'HTTP',status,'code',result.get('code','rpc') if isinstance(result,dict) else '-',flush=True)
    return status,rh,result
def ok(r):
    if r[0]!=200 or not isinstance(r[2],dict) or r[2].get('code')!=0: raise RuntimeError('Unexpected application failure; see redacted evidence')
    return r[2].get('data')
def login_admin():
    r=call('admin:login','/api/v1/admin/login',{'email':ENV['DEFAULT_SUPERUSER_EMAIL'],'password':enc(ENV['ADMIN_DEFAULT_PASSWORD'])})
    ok(r); S['admin_token']=r[1].get('Authorization') or r[1].get('authorization'); assert S['admin_token']; save()
def login_owner():
    r=call('owner-session:login','/api/v1/auth/login',{'email':S['email'],'password':enc(S['password'])})
    ok(r); S['owner_token']=r[1].get('Authorization') or r[1].get('authorization'); assert S['owner_token']; save()
def rpc(label,method,params,token=None,direct=True):
    return call(label,'/api/v1/mcp',{'jsonrpc':'2.0','id':len(E['events'])+1,'method':method,'params':params},token,direct=direct,headers={'MCP-Protocol-Version':'2025-03-26'})
def setup():
    assert not S.get('created'),'Already set up'
    S.update(email='codex-validation-'+secrets.token_hex(5)+'@ragflow.local',password=secrets.token_urlsafe(24),prefix='CODEX-VALIDATION-'+secrets.token_hex(4),datasets=[])
    save(); login_admin()
    user=ok(call('admin:create-test-user','/api/v1/admin/users',{'username':S['email'],'password':enc(S['password']),'role':'user'},S['admin_token']))
    S['created']=True; save(); login_owner()
    keys=ok(call('owner-session:create-key','/api/v1/system/tokens',{'name':S['prefix']},S['owner_token']))
    S['api_token']=keys['token']; S['beta_token']=keys['beta']; save()
    lm=json.loads((ROOT/'config/lmstudio.json').read_text())
    ok(call('owner-session:add-provider','/api/v1/providers',{'provider_name':lm['provider']},S['owner_token'],method='PUT'))
    ok(call('owner-session:add-instance','/api/v1/providers/'+urllib.parse.quote(lm['provider'],safe='')+'/instances',{'instance_name':lm['instance'],'api_key':'','base_url':lm['base_url'],'region':'default','model_info':[{'model_name':lm['model'],'model_type':['embedding'],'max_tokens':lm['max_tokens'],'extra':{'max_dimension':lm['dimensions'],'max_batch_size':8}}]},S['owner_token']))
    ok(call('owner-session:embedding-default','/api/v1/models/default',{'model_provider':lm['provider'],'model_instance':lm['instance'],'model_name':lm['model'],'model_type':'embedding'},S['owner_token'],method='PATCH'))
    for label in ('A-SHARED','B-PRIVATE'):
        d=ok(call('owner-session:create-'+label,'/api/v1/datasets',{'name':S['prefix']+'-'+label,'parse_type':1,'parser_id':'general','embedding_model':lm['model']+'@'+lm['instance']+'@'+lm['provider'],'permission':'me','language':'English'},S['owner_token']))
        S['datasets'].append(d['id']); save()
    chat=ok(call('owner-session:create-app-A','/api/v1/chats',{'name':S['prefix']+'-APP-A','dataset_ids':[S['datasets'][0]]},S['owner_token']))
    S['chat_id']=chat['id']; save()
    ok(call('owner-session:verify-app-A-scope','/api/v1/chats/'+S['chat_id'],token=S['owner_token']))
    ok(call('beta:shared-app-info','/api/v1/chatbots/'+S['chat_id']+'/info',token=S['beta_token']))
def ingest():
    lm=json.loads((ROOT/'config/lmstudio.json').read_text())
    S.setdefault('documents',{})
    S.setdefault('marker','CODEX_PRIVATE_'+secrets.token_hex(10)); save()
    for index,label in enumerate(('A-SHARED','B-PRIVATE')):
        d=S['datasets'][index]
        if label not in S['documents']:
            boundary='----CodexValidation'+secrets.token_hex(8)
            content=('Synthetic public document for shared app A.' if index==0 else 'Synthetic private test document. Marker: '+S['marker']+'. This text belongs only to dataset B and must never be visible to recipients of shared app A.')+'\n'
            payload=('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="'+label.lower()+'.txt"\r\nContent-Type: text/plain\r\n\r\n'+content+'\r\n--'+boundary+'--\r\n').encode()
            docs=ok(call('owner-session:upload-'+label,'/api/v1/datasets/'+d+'/documents',payload,S['owner_token'],content_type='multipart/form-data; boundary='+boundary))
            S['documents'][label]=docs[0]['id']; save()
            ok(call('owner-session:parse-'+label,'/api/v1/datasets/'+d+'/chunks',{'document_ids':[docs[0]['id']]},S['owner_token']))
        r=ok(call('owner-session:document-status-'+label,'/api/v1/datasets/'+d+'/documents',token=S['owner_token']))
        print(json.dumps([{'id':x['id'],'status':x.get('ingestion_status'),'chunks':x.get('chunk_count')} for x in r.get('docs',[])],ensure_ascii=False),flush=True)
def fulltext():
    for i,label in enumerate(('A-SHARED','B-PRIVATE')):
        d=S['datasets'][i]
        info=ok(call('owner-session:read-config-'+label,'/api/v1/datasets/'+d,token=S['owner_token']))
        cfg=info['parser_config']; cfg['Tokenizer:LegalReadersDecide']['search_method']=['full_text']
        ok(call('owner-session:fulltext-only-'+label,'/api/v1/datasets/'+d,{'parser_config':cfg},S['owner_token'],method='PUT'))
        ok(call('owner-session:document-fulltext-only-'+label,'/api/v1/datasets/'+d+'/documents/'+S['documents'][label],{'parser_config':cfg},S['owner_token'],method='PATCH'))
        ok(call('owner-session:reparse-fulltext-'+label,'/api/v1/datasets/'+d+'/chunks',{'document_ids':[S['documents'][label]]},S['owner_token']))
def app():
    chat=ok(call('owner-session:create-app-A-ready','/api/v1/chats',{'name':S['prefix']+'-APP-A','dataset_ids':[S['datasets'][0]]},S['owner_token']))
    S['chat_id']=chat['id']; save()
    ok(call('owner-session:verify-app-A-scope','/api/v1/chats/'+S['chat_id'],token=S['owner_token']))
    ok(call('beta:shared-app-info','/api/v1/chatbots/'+S['chat_id']+'/info',token=S['beta_token']))
def f01():
    init={'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'codex-authorized-lab-validation','version':'1'}}
    rpc('beta:gateway-init','initialize',init,S['beta_token'],False)
    rpc('no-token:direct-init','initialize',init)
    rpc('invalid-token:direct-init','initialize',init,'invalid-codex-validation')
    rpc('beta:direct-init','initialize',init,S['beta_token'])
    rpc('beta:tools-list','tools/list',{},S['beta_token'])
    rpc('beta:list-datasets','tools/call',{'name':'ragflow_list_datasets','arguments':{'page':1,'page_size':20}},S['beta_token'])
    call('beta:ordinary-dataset-route-negative','/api/v1/datasets/'+S['datasets'][1],token=S['beta_token'])
    ok(call('api:owner-positive-private-dataset','/api/v1/datasets/'+S['datasets'][1],token=S['api_token']))
    if S.get('marker'):
        rpc('beta:retrieve-private-B','tools/call',{'name':'ragflow_retrieval','arguments':{'dataset_ids':[S['datasets'][1]],'question':S['marker'],'similarity_threshold':0,'vector_similarity_weight':0,'page_size':3}},S['beta_token'])
def f02():
    d=S['datasets'][1]
    ok(call('api:before-deactivation-private-dataset','/api/v1/datasets/'+d,token=S['api_token']))
    ok(call('owner-session:before-deactivation-private-dataset','/api/v1/datasets/'+d,token=S['owner_token']))
    ok(call('beta:before-deactivation-app-info','/api/v1/chatbots/'+S['chat_id']+'/info',token=S['beta_token']))
    call('no-token:private-dataset','/api/v1/datasets/'+d)
    ok(call('admin:deactivate-test-user','/api/v1/admin/users/'+S['email']+'/activate',{'activate_status':'off'},S['admin_token'],method='PUT'))
    ok(call('admin:confirm-inactive','/api/v1/admin/users/'+S['email'],token=S['admin_token']))
    call('owner-session:after-deactivation','/api/v1/datasets/'+d,token=S['owner_token'])
    call('password:after-deactivation-login','/api/v1/auth/login',{'email':S['email'],'password':enc(S['password'])})
    call('api:after-deactivation-private-dataset','/api/v1/datasets/'+d,token=S['api_token'])
    call('beta:after-deactivation-app-info','/api/v1/chatbots/'+S['chat_id']+'/info',token=S['beta_token'])
    rpc('beta:after-deactivation-list-datasets','tools/call',{'name':'ragflow_list_datasets','arguments':{'page':1,'page_size':20}},S['beta_token'])
    if S.get('marker'):
        rpc('beta:after-deactivation-retrieve-B','tools/call',{'name':'ragflow_retrieval','arguments':{'dataset_ids':[d],'question':S['marker'],'similarity_threshold':0,'vector_similarity_weight':0,'page_size':3}},S['beta_token'])
def postdata():
    path='/api/v1/datasets/'+S['datasets'][1]+'/documents/'+S['documents']['B-PRIVATE']
    r=call('api:after-deactivation-download-private-document',path,token=S['api_token'])
    assert r[0]==200 and S['marker'] in str(r[2]), 'Private document marker not returned'
    E['private_document_download_after_deactivation']=True; save()
def cleanup():
    if not S.get('created'): return
    assert S['email'].startswith('codex-validation-') and S['email'].endswith('@ragflow.local')
    ok(call('admin:reactivate-for-cleanup','/api/v1/admin/users/'+S['email']+'/activate',{'activate_status':'on'},S['admin_token'],method='PUT'))
    login_owner()
    if S.get('chat_id'): ok(call('owner-session:delete-test-app','/api/v1/chats/'+S['chat_id'],token=S['owner_token'],method='DELETE'))
    if S.get('datasets'): ok(call('owner-session:delete-test-datasets','/api/v1/datasets',{'ids':S['datasets']},S['owner_token'],method='DELETE'))
    ok(call('owner-session:revoke-test-key','/api/v1/system/tokens/'+urllib.parse.quote(S['api_token'],safe=''),token=S['owner_token'],method='DELETE'))
    call('api:after-key-revocation','/api/v1/datasets',token=S['api_token'])
    rpc('beta:after-key-revocation','tools/list',{},S['beta_token'])
    ok(call('admin:deactivate-for-deletion','/api/v1/admin/users/'+S['email']+'/activate',{'activate_status':'off'},S['admin_token'],method='PUT'))
    ok(call('admin:delete-test-user','/api/v1/admin/users/'+S['email'],token=S['admin_token'],method='DELETE'))
    call('admin:confirm-test-user-removed','/api/v1/admin/users/'+S['email'],token=S['admin_token'])
    E['cleanup']='Synthetic app, both datasets/documents, API/beta key and test user removed through real APIs.'
    S['created']=False; save()
    STATE.unlink()
if __name__=='__main__':
    action=sys.argv[1]
    if action=='status': print(json.dumps({'email':S.get('email'),'datasets':S.get('datasets'),'document_id':S.get('document_id'),'events':len(E['events'])}))
    else:
        try: globals()[action]()
        except Exception as error:
            print(type(error).__name__+': '+scrub(str(error)),file=sys.stderr); sys.exit(1)
