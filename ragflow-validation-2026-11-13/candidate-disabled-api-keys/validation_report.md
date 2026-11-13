# Runtime validation — 2026-11-13

Method: realistic local HTTP reproduction against the existing authorized lab, using synthetic objects only. No code/configuration patch applied. The completed 2026-11-10 scan remains immutable.

Runtime: Go RAGFlow v1.0.0-rc3, image reference docker.io/infiniflow/ragflow@sha256:931307991475344f61c0d2f2af4c10dd5b37a3cdfa5814737688b8bb8f6a7298; source snapshot declared by lab README: 03c1246150febe6b204b3799dffb3afe52103fb8. Original scan source: 8cab68a9a3b083da95abb2ea0789b0a5623defaf. Image/source byte-for-byte equivalence is not claimed. Web: http://127.0.0.1:18080/; admin /admin; direct API loopback inside container :9380 only.

## F02: API and beta keys survive account deactivation

Candidate id: candidate-disabled-api-keys
Instance key: disabled-api-keys
Ledger row id: not provided by original Standard scan.
Original root-control: internal/service/user.go:776–795
Lab root-control: upstream/internal/service/user.go:907–930
Advisory/source: prior completed local scan b25a7472-7c3e-483f-bc74-7eebcb9723ea, findings.json; no external advisory seed supplied.
Confidence: high for the observed boundary failure; scope limits below.
Disposition: reportable; survives: yes.

### Rubric

- [x] Enabled API, beta, session and unauthenticated baselines established through real HTTP routes.
- [x] Synthetic user deactivated through admin API and independently confirmed inactive.
- [x] The same old API/beta credentials remained usable; private document bytes returned to API key.
- [x] Old web session and fresh password login rejected, isolating credential-specific deactivation failure.
- [x] Synthetic objects/user/key removed; explicit key revocation rejected both API and beta credentials.

### Observed evidence

After PUT /api/v1/admin/users/<synthetic-user>/activate {activate_status:off}, independent GET admin/users confirmed is_active:0. The preexisting web session returned HTTP 401; a new password login returned HTTP 200/code403 disabled. The unchanged API key still read private dataset B (HTTP 200/code0) and downloaded B's original text, including unique synthetic marker CODEX_PRIVATE_e0b02e8db69767e8ac8d, through Nginx. The unchanged beta key still read shared-app info (HTTP 200/code0) through Nginx and listed both datasets through diagnostic container-loopback MCP. No new key was issued after deactivation.

Evidence event labels: api:before-deactivation-private-dataset, admin:deactivate-test-user, admin:confirm-inactive, owner-session:after-deactivation, password:after-deactivation-login, api:after-deactivation-private-dataset, beta:after-deactivation-app-info, beta:after-deactivation-list-datasets, api:after-deactivation-download-private-document, api:after-key-revocation, beta:after-key-revocation.

### Uncertainty and next step

The proven scope is the deactivated user's own previously authorized data, not arbitrary other tenants. MCP text retrieval was blocked by the offline embedding dependency. Reactivation/key-reissue policy and a remediated build were not tested; no patch was applied.

Minimal additional proof for full MCP content retrieval: restore the lab's real local embedding service, rerun with synthetic fixtures and verify returned marker, retaining the same gateway distinction. No application build or sanitizer/debugger was required for these HTTP authorization defects.

### Artifacts and cleanup

Redacted HTTP evidence: ../evidence.json. Actual executed harness: ../executed-validation.py. Reproduction guide: ../README.txt.

Synthetic app, both datasets and their documents, provider configuration (through user removal), test account and API/beta key were removed through application APIs. Explicit key revocation yielded API HTTP401 and beta HTTP200/code102. Admin GET then returned code404 User not found. Temporary credential state was deleted. The existing lab health check passed after cleanup.
