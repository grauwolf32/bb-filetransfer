RAGFlow F01/F02 runtime validation — 2026-11-13

report.html — Russian HTML report.
evidence.json — 71 redacted actual HTTP observations.
executed-validation.py — actual final harness used in this session (SHA256 8d7373c2b88a424f6ccdb724bd65ee35a2b30d8a870a606c3aa6cd123d7dd0df).
reproduce.py — reordered helper for a fresh reproduction. Syntax checked only; not rerun end-to-end.
validation.json — explicit per-candidate results and 18 beta routes.

Target is hard-coded to /Users/ruslan/recent-work/ragflow, localhost port from its .env, and existing lab.sh. Do not point this helper at production. It creates and deletes only a randomly named synthetic user and its own objects. Admin login rotates that admin's session as in ordinary RAGFlow login.
Do not run helpers directly in the exported directory: use a private disposable staging directory, because private-state.json temporarily holds test credentials.

Fresh reproduction using reproduce.py:
1. Copy reproduce.py into a private temporary directory (chmod 700 directory); use umask 077.
2. python3 reproduce.py setup
3. python3 reproduce.py ingest
4. Repeat ingest after a few seconds until both synthetic docs show COMPLETED/chunks>=1. It uses full-text-only tokenization, with no fabricated embeddings.
5. python3 reproduce.py app
6. python3 reproduce.py f01
7. python3 reproduce.py f02
8. python3 reproduce.py postdata
9. python3 reproduce.py cleanup
If anything fails, inspect the redacted evidence locally and run cleanup before deleting the private state. Do not share private-state.json.
The executed session originally tried default embedding ingestion. It failed because the configured LM Studio service at localhost:1235 was stopped. After fulltext changed dataset config, document configs were updated too and reparsed. Therefore actual evidence has failed setup/ingestion attempts followed by successful fixtures.

F01 proves private dataset metadata disclosure via API MCP when reached directly inside the container; nginx on :18080 rejects the path with 404. Text retrieval was attempted and failed at the real embedding dependency. No claim of successful MCP content exfiltration is made.
F02 additionally proves original private-document bytes returned by an unchanged API key after independent admin confirmation is_active=0, through the normal nginx route. Session and password-login negative controls worked.
Explicit key revocation then rejected API and beta; synthetic app, datasets/documents, user and temporary credential state were removed. lab.sh check passed.
No source patch, runtime image change, reverse proxy change or existing dataset change was performed.
