# Threat Model

RAGFlow Go deployment: browser/API → Nginx → API; separate Admin, ingestors and syncer; MySQL metadata, MinIO objects, Elasticsearch chunks/vectors, Kvrocks state and NATS work queue. Current src tree has no root legacy Python services; AGENTS migration inventory is stale. Docker starts Go services (docker/entrypoint.sh:164-186).

## Assets

- Private documents, chunks, embeddings, chats and tool credentials; ownership and team scopes (internal/permission/policy.go:104-168).
- RAGFLOW_SECRET_KEY or Kvrocks-generated signing secret; persisted user sessions/API/Beta tokens (internal/server/variable.go:91-169; internal/service/user.go:747-800).
- Model API keys and base URLs reach selected drivers (internal/service/model_factory.go:848-861); bootstrap admin credential can be retained as logs/admin_bootstrap_password.txt with mode 0600 and exposed to log-volume/backup readers (internal/admin/service.go:1339-1447; docker/docker-compose.yml:35).

## Trust Boundaries

- Internet/LAN to Nginx and direct API/Admin listeners: parsed api.host/admin.host are ignored by listener addresses ':port' (internal/server/api/server.go:376-399; internal/server/admin/server.go:85-112).
- Users and API/share-token holders to tenant resources: HMAC session validation and DB token resolution, community ownership/team policy. Beta scope is lost at MCP and disabled-user state is not enforced for API/beta credentials; both were source validated (internal/handler/auth.go:103-149; internal/service/user.go:747-800).
- Services to data infrastructure: ES skips certificate verification; NATS uses nats:// with host/port only; Kvrocks client has password but omits parsed username/TLS (internal/engine/elasticsearch/client.go:45-56; internal/engine/nats/nats.go:78-81; internal/engine/kvrocks/redis.go:170-174).
- Documents and model/tool outputs to parsers and agent execution: local sandbox explicitly has no isolation; self-managed manager has Docker socket/privileged container (internal/agent/sandbox/local.go:20-25; docker/docker-compose-base.yml:228-257).
- External MCP client → optional standalone listener defaults disabled/loopback and self-host mode with configured shared identity; host mode resolves per-caller credentials. API /api/v1/mcp exists independently (internal/server/config/mcp_config.go:40-78; internal/handler/mcp_server.go:64-106). Outgoing MCP independently validates URLs/pins DNS and rejects credential headers on HTTP (internal/mcp/client/mcp_call.go:82-100).
- Model destination policies differ: LM Studio permits empty API key and uses scheme-only HTTP guard, so ALLOW_ANY_HOST=0 does not prohibit all private outbound connections (internal/entity/models/lmstudio.go:35-42; internal/common/http.go:124-144). Provider receives prompts/retrieved chunks; tracing and logs are separate recipients.

## Attacker Capabilities

- Anonymous visitor controls login/registration, configured public webhooks and share links but not admin/operator state (internal/router/router.go:154-222).
- Ordinary or former tenant user controls uploads/resource IDs/agent inputs/API tokens; malicious source owner controls retrieved document text. On-path attacker is conditional on network access.

## Security Objectives

- Preserve per-user/tenant resource access and share-token resource scope on every endpoint, including MCP.
- Disabled identities and disallowed login methods fail closed; keep Admin/state services private and TLS validated.
- Treat documents/model output as data; restrict execution authority, egress and quotas independently of prompts.

## Assumptions

- Focused static hardening review; repository scope is broad and full file-by-file coverage is not claimed; runtime deployment and image binary parity not tested.
- Local laboratory is a separate v1.0.0-rc3 snapshot per README at /Users/ruslan/recent-work/ragflow/upstream; actual running state not inspected.
- OSS has no OAuth login or operation audit sink: !ee stubs internal/server/config/stub.go:90-100 and internal/common/stub.go:36-60. DISABLE_PASSWORD_LOGIN is parsed/exposed; backend enforcement is absent in the inspected login path.
- Local lab config restricts host publication to 127.0.0.1:18080, disables registration/MCP at proxy, pins images and private backend network (external deployment evidence compose.yaml:18-57,195-198).
- MinIO Verify defaults false despite template comment; explicit secure:true, verify:true needed. MySQL DSN omits TLS; Kvrocks username/TLS omitted; NATS host/port config has no dedicated credential/TLS options (internal/server/config/storage_engine_config.go:77-85; internal/storage/minio.go:57-68; internal/dao/database.go:325-335; internal/engine/kvrocks/redis.go:170-174; internal/server/config/queue_engine_config.go:29-33).
- Docker publishes port 443 but default Nginx only listens HTTP :80. CLI explicit config or ./conf, '.', /etc/ragflow search plus parser-specific env lookup: do not assume all RAGFLOW_<SECTION>_<KEY> overrides work uniformly (docker/nginx/ragflow.conf:1-4; internal/server/config.go:40-59).
- Source-validated findings: beta share credentials lose scope at MCP; disabled users retain API/beta keys; password-disable setting is not enforced; admin reset preserves old sessions; API/Admin bind hosts ignored; ES TLS validation disabled; MinIO verification unsafe default. Lab source mechanisms compared; image runtime untested.

---

## Saved Model Context

- Source: scan
- Scan: b25a7472-7c3e-483f-bc74-7eebcb9723ea
- Target: ragflow
- Revision: 8cab68a9a3b083da95abb2ea0789b0a5623defaf
- Result status: completed
- Model origin: not recorded
- Model scope: not recorded
- Scan scope: .
- Scan scope description: Focused static security configuration and hardening assessment of Go OSS with independent source review. Supplementary Russian HTML is hardening/ragflow-security-report.html; decision portfolio is hardening/hardening.md. Separately authorized local lab snapshot and official online documentation are contextual evidence.
