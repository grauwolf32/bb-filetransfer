# Runtime validation — 2026-11-13

Method: realistic local HTTP reproduction against the existing authorized lab, using synthetic objects only. No code/configuration patch applied. The completed 2026-11-10 scan remains immutable.

Runtime: Go RAGFlow v1.0.0-rc3, image reference docker.io/infiniflow/ragflow@sha256:931307991475344f61c0d2f2af4c10dd5b37a3cdfa5814737688b8bb8f6a7298; source snapshot declared by lab README: 03c1246150febe6b204b3799dffb3afe52103fb8. Original scan source: 8cab68a9a3b083da95abb2ea0789b0a5623defaf. Image/source byte-for-byte equivalence is not claimed. Web: http://127.0.0.1:18080/; admin /admin; direct API loopback inside container :9380 only.

## F01: Public share beta token gains owner's MCP scope

Candidate id: candidate-beta-mcp
Instance key: share-beta-mcp
Ledger row id: not provided by original Standard scan.
Original root-control: internal/handler/mcp_server.go:99–106
Lab root-control: upstream/internal/handler/mcp_server.go:98–106
Advisory/source: prior completed local scan b25a7472-7c3e-483f-bc74-7eebcb9723ea, findings.json; no external advisory seed supplied.
Confidence: high for the observed boundary failure; scope limits below.
Disposition: reportable; survives: yes.

### Rubric

- [x] Running Go image/version and distinction from scanned source established.
- [x] Synthetic A-only app, private B, and real beta issuance/app-info baseline established.
- [x] Real MCP initialize, tools/list and list-datasets demonstrated B metadata; invalid/absent-token and ordinary-route controls executed.
- [x] Gateway reachability tested separately: HTTP 404 versus successful container-loopback API requests.
- [x] Synthetic objects and credentials removed; remaining text-retrieval gap stated.

### Observed evidence

The same beta key accepted by GET /api/v1/chatbots/<app-A>/info initialized API MCP and returned the private B dataset ID and name from tools/list and ragflow_list_datasets. A was configured with only dataset A. No owner session/API credential was provided to the beta requests. An invalid or absent key returned application code 102; beta on ordinary GET /datasets/<B> returned HTTP 401. The normal Nginx MCP request returned HTTP 404.

Evidence event labels: beta:gateway-init, no-token:direct-init, invalid-token:direct-init, beta:direct-init, beta:tools-list, beta:list-datasets, beta:ordinary-dataset-route-negative, beta:retrieve-private-B.

### Uncertainty and next step

Actual document-text retrieval through MCP was attempted twice and returned isError:true: the configured local embedding endpoint refused the connection. Thus MCP metadata disclosure/scope escalation is dynamically confirmed; successful text retrieval is not. Direct API tests were inside the container and bypassed Nginx; the lab gateway blocks this MCP path.

Minimal additional proof for full MCP content retrieval: restore the lab's real local embedding service, rerun with synthetic fixtures and verify returned marker, retaining the same gateway distinction. No application build or sanitizer/debugger was required for these HTTP authorization defects.

### Artifacts and cleanup

Redacted HTTP evidence: ../evidence.json. Actual executed harness: ../executed-validation.py. Reproduction guide: ../README.txt.

Synthetic app, both datasets and their documents, provider configuration (through user removal), test account and API/beta key were removed through application APIs. Explicit key revocation yielded API HTTP401 and beta HTTP200/code102. Admin GET then returned code404 User not found. Temporary credential state was deleted. The existing lab health check passed after cleanup.
