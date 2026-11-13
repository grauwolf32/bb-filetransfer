# F01/F02 lab validation rubric — 2026-11-13

Scope: the existing authorized local RAGFlow lab at /Users/ruslan/recent-work/ragflow. Preserve the completed 2026-11-10 scan; retain this follow-up separately. Use synthetic accounts/datasets only. Do not change gateway restrictions. Do not log passwords, bearer/API/beta credentials or existing document contents.

## F01 / candidate-beta-mcp / share-beta-mcp

Attacker input: a beta credential normally included in an embed/share URL. Preconditions: a publisher account with a shared app A, unrelated private dataset B, and access to the API MCP route. Sink: owner-scoped dataset listing/retrieval at /api/v1/mcp. Original root: internal/handler/mcp_server.go:99–106.

- [ ] Establish running image/version and whether it matches the reviewed Go source; report differences.
- [ ] Create isolated publisher/app A and unrelated private B; obtain beta through the actual token/share path, with no existing owner credential supplied to attacker requests.
- [ ] Reproduce MCP initialize/tools/list and unauthorized listing or retrieval of B using beta, with invalid/no-token controls and owner positive control.
- [ ] Test the normal lab gateway separately; any direct container-loopback test is marked as bypassing gateway for diagnostic purposes and does not prove external exploitability.
- [ ] Remove synthetic objects/credentials; record observations, exact gaps, and a separate disposition for product behavior and lab reachability.

## F02 / candidate-disabled-api-keys / disabled-api-keys

Attacker input: API/beta credentials issued to a formerly enabled account. Preconditions: synthetic user, its own synthetic data, valid keys and administrator access for deactivation. Sink: authenticated dataset/read or beta endpoint after deactivation. Original root: internal/service/user.go:776–795.

- [ ] Verify enabled baseline with API/beta/session credentials over actual HTTP endpoints and unauthenticated control.
- [ ] Deactivate only the synthetic user through the real admin API; independently confirm inactive state.
- [ ] Retry the same old API and beta credentials after deactivation against protected data, without new keys or impersonation.
- [ ] Check old-session and fresh-password-login rejection to distinguish missing deactivation from credential-specific bypass; record any version/route differences.
- [ ] Revoke/delete synthetic credentials and data/account and record cleanup and residual uncertainty.
