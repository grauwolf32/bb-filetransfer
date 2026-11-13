# Validation closure — 2026-11-13

The two requested instances were validated against the existing v1.0.0-rc3 lab using realistic HTTP requests and synthetic data. Original sealed scan unchanged. Each instance has a separate validation report and ledger receipt.

| Ledger row id | Instance key | Source / advisory | Seed anchor | Root control (original scan) | Entrypoint / source | Sink / control | Disposition | Counterevidence or proof gap | Survives |
|---|---|---|---|---|---|---|---|---|---|
| not supplied | share-beta-mcp / candidate-beta-mcp | Prior scan b25a7472-7c3e-483f-bc74-7eebcb9723ea | none | internal/handler/mcp_server.go:99–106 | beta → POST /api/v1/mcp | owner-scoped MCP dataset list | reportable | Nginx rejects MCP with 404; internal diagnostic API exposes private B metadata. MCP text retrieval failed because real embedding endpoint was offline. | yes |
| not supplied | disabled-api-keys / candidate-disabled-api-keys | Prior scan b25a7472-7c3e-483f-bc74-7eebcb9723ea | none | internal/service/user.go:776–795 | unchanged API/beta keys after admin deactivation | identity resolver / private original document download | reportable | Session and password controls reject; API key reads synthetic document through normal gateway. Scope limited to previous user's data. | yes |

See candidate-beta-mcp/validation_report.md and candidate-disabled-api-keys/validation_report.md for rubrics, evidence labels, uncertainty and minimal next steps. The HTML supplement and 71 redacted observations are in this directory. Synthetic fixtures and temporary credential state were removed; lab health passed. Proposed beta-disable code was not applied or verified.
