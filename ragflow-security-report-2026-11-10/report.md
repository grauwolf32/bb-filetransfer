# Security Review: ragflow

## Scope

Focused static security configuration and hardening assessment of Go OSS with independent source review. Supplementary Russian HTML is hardening/ragflow-security-report.html; decision portfolio is hardening/hardening.md. Separately authorized local lab snapshot and official online documentation are contextual evidence.

- Scan mode: repository
- Target kind: git_revision
- Target ID: target_sha256_03972abe1556a7f941d2ed780858d4bc4853d5ff0847aaee82d14648ac77d3fc
- Revision: 8cab68a9a3b083da95abb2ea0789b0a5623defaf
- Inventory strategy: repository
- Included paths: .
- Excluded paths: none
- Artifacts reviewed: docker/docker-compose.yml, docker/service_conf.yaml.template, internal/handler/auth.go, internal/service/user.go, internal/handler/mcp_server.go, internal/handler/mcp_retrieval.go, internal/server/api/server.go, internal/server/admin/server.go, internal/engine/elasticsearch/client.go, internal/server/config/storage_engine_config.go, internal/storage/minio.go, hardening/ragflow-security-report.html, hardening/hardening.md, hardening/hardening.json, report_validation.md
- Scan context: User requested security settings, hardening, infrastructure verification, threat model and HTML. No source/config mutations or production testing authorized/required by this review.

Limitations and exclusions:
- Focused partial source coverage; no full repository/native/dependency/container audit.
- Local lab source snapshot compared for critical mechanisms; actual image binary parity and running state not verified.
- No production changes, service restarts, exploit inputs or load tests performed.
- Detailed OSS audit and OAuth/SSO implementations are absent; enterprise implementation not inspected.
- Excluded internal/binding/cpp/\*\*: Native implementation not exhaustively reviewed; parser containment and image/native dependency verification remain staging work.
- Excluded test/\*\*: Tests consulted as supporting material only; no full test corpus audit or application execution.

### Scan Summary

| Field | Value |
| --- | --- |
| Scan outcome | completed |
| Reportable findings | 7 |
| Severity mix | high: 2, medium: 5 |
| Confidence mix | high: 7 |
| Coverage | partial |
| Validation mode | Static source-backed validation; independent baseline and auth review reconciled by parent. |

Canonical artifacts: `scan-manifest.json`, `findings.json`, and `coverage.json`. This report is a deterministic projection of those files.

## Threat Model

RAGFlow Go deployment: browser/API → Nginx → API; separate Admin, ingestors and syncer; MySQL metadata, MinIO objects, Elasticsearch chunks/vectors, Kvrocks state and NATS work queue. Current src tree has no root legacy Python services; AGENTS migration inventory is stale. Docker starts Go services (docker/entrypoint.sh:164-186).

### Assets

- Private documents, chunks, embeddings, chats and tool credentials; ownership and team scopes (internal/permission/policy.go:104-168).
- RAGFLOW_SECRET_KEY or Kvrocks-generated signing secret; persisted user sessions/API/Beta tokens (internal/server/variable.go:91-169; internal/service/user.go:747-800).
- Model API keys and base URLs reach selected drivers (internal/service/model_factory.go:848-861); bootstrap admin credential can be retained as logs/admin_bootstrap_password.txt with mode 0600 and exposed to log-volume/backup readers (internal/admin/service.go:1339-1447; docker/docker-compose.yml:35).

### Trust Boundaries

- Internet/LAN to Nginx and direct API/Admin listeners: parsed api.host/admin.host are ignored by listener addresses ':port' (internal/server/api/server.go:376-399; internal/server/admin/server.go:85-112).
- Users and API/share-token holders to tenant resources: HMAC session validation and DB token resolution, community ownership/team policy. Beta scope is lost at MCP and disabled-user state is not enforced for API/beta credentials; both were source validated (internal/handler/auth.go:103-149; internal/service/user.go:747-800).
- Services to data infrastructure: ES skips certificate verification; NATS uses nats:// with host/port only; Kvrocks client has password but omits parsed username/TLS (internal/engine/elasticsearch/client.go:45-56; internal/engine/nats/nats.go:78-81; internal/engine/kvrocks/redis.go:170-174).
- Documents and model/tool outputs to parsers and agent execution: local sandbox explicitly has no isolation; self-managed manager has Docker socket/privileged container (internal/agent/sandbox/local.go:20-25; docker/docker-compose-base.yml:228-257).
- External MCP client → optional standalone listener defaults disabled/loopback and self-host mode with configured shared identity; host mode resolves per-caller credentials. API /api/v1/mcp exists independently (internal/server/config/mcp_config.go:40-78; internal/handler/mcp_server.go:64-106). Outgoing MCP independently validates URLs/pins DNS and rejects credential headers on HTTP (internal/mcp/client/mcp_call.go:82-100).
- Model destination policies differ: LM Studio permits empty API key and uses scheme-only HTTP guard, so ALLOW_ANY_HOST=0 does not prohibit all private outbound connections (internal/entity/models/lmstudio.go:35-42; internal/common/http.go:124-144). Provider receives prompts/retrieved chunks; tracing and logs are separate recipients.

### Attacker Capabilities

- Anonymous visitor controls login/registration, configured public webhooks and share links but not admin/operator state (internal/router/router.go:154-222).
- Ordinary or former tenant user controls uploads/resource IDs/agent inputs/API tokens; malicious source owner controls retrieved document text. On-path attacker is conditional on network access.

### Security Objectives

- Preserve per-user/tenant resource access and share-token resource scope on every endpoint, including MCP.
- Disabled identities and disallowed login methods fail closed; keep Admin/state services private and TLS validated.
- Treat documents/model output as data; restrict execution authority, egress and quotas independently of prompts.

### Assumptions

- Focused static hardening review; repository scope is broad and full file-by-file coverage is not claimed; runtime deployment and image binary parity not tested.
- Local laboratory is a separate v1.0.0-rc3 snapshot per README at /Users/ruslan/recent-work/ragflow/upstream; actual running state not inspected.
- OSS has no OAuth login or operation audit sink: !ee stubs internal/server/config/stub.go:90-100 and internal/common/stub.go:36-60. DISABLE_PASSWORD_LOGIN is parsed/exposed; backend enforcement is absent in the inspected login path.
- Local lab config restricts host publication to 127.0.0.1:18080, disables registration/MCP at proxy, pins images and private backend network (external deployment evidence compose.yaml:18-57,195-198).
- MinIO Verify defaults false despite template comment; explicit secure:true, verify:true needed. MySQL DSN omits TLS; Kvrocks username/TLS omitted; NATS host/port config has no dedicated credential/TLS options (internal/server/config/storage_engine_config.go:77-85; internal/storage/minio.go:57-68; internal/dao/database.go:325-335; internal/engine/kvrocks/redis.go:170-174; internal/server/config/queue_engine_config.go:29-33).
- Docker publishes port 443 but default Nginx only listens HTTP :80. CLI explicit config or ./conf, '.', /etc/ragflow search plus parser-specific env lookup: do not assume all RAGFLOW_\<SECTION\>_\<KEY\> overrides work uniformly (docker/nginx/ragflow.conf:1-4; internal/server/config.go:40-59).
- Source-validated findings: beta share credentials lose scope at MCP; disabled users retain API/beta keys; password-disable setting is not enforced; admin reset preserves old sessions; API/Admin bind hosts ignored; ES TLS validation disabled; MinIO verification unsafe default. Lab source mechanisms compared; image runtime untested.

## Findings

| Finding | Severity | Confidence | Detailed write-up |
| --- | --- | --- | --- |
| [API and beta keys survive account deactivation](#finding-1) | high | high | inline below |
| [Public share beta tokens gain the owner's MCP retrieval scope](#finding-2) | high | high | inline below |
| [Administrative password reset leaves existing sessions valid](#finding-3) | medium | high | inline below |
| [Disabling password login does not block password authentication](#finding-4) | medium | high | inline below |
| [API and Admin listeners ignore configured bind hosts](#finding-5) | medium | high | inline below |
| [MinIO HTTPS defaults to disabled certificate verification](#finding-6) | medium | high | inline below |
| [Elasticsearch HTTPS client skips certificate verification](#finding-7) | medium | high | inline below |

### Confidence Scale

| Label | Meaning |
| --- | --- |
| high | Direct evidence supports the finding with no material unresolved blocker. |
| medium | Evidence supports a plausible issue, but material runtime or reachability proof remains. |
| low | Evidence is incomplete and the item is retained only for explicit follow-up. |

<a id="finding-1"></a>

### [1] API and beta keys survive account deactivation

| Field | Value |
| --- | --- |
| Severity | high |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Account deactivation bypass |
| CWE | CWE-863 |
| Affected lines | internal/admin/service.go:456-467, internal/dao/api_token.go:48-74, internal/service/user.go:776-795, internal/service/stub.go:74-81, internal/handler/auth.go:172-180, internal/handler/common.go:79-90 |

#### Summary

An administratively deactivated user can continue authenticating with previously issued API/beta keys because account state is not checked by their identity resolver.

#### Root Cause

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. Deactivation revokes the stored session identifier but keeps API/beta rows; API identity resolution only requires the session identifier to be nonempty.

**Trace: internal/admin/service.go** — `internal/admin/service.go:456-467`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/admin/service.go transition.

```go
	if user.IsActive == targetStatus {
		return nil
	}

	user.IsActive = targetStatus
	if !isActive {
		invalidToken := "INVALID_" + common.GenerateToken()
		user.AccessToken = &invalidToken
	}

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return fmt.Errorf("failed to update user: %w", err)
```

**Trace: internal/dao/api_token.go** — `internal/dao/api_token.go:48-74`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/dao/api_token.go transition.

```go
	var apiToken entity.APIToken
	tx := db.WithContext(ctx).Where("token = ?", token).Find(&apiToken)
	if tx.Error != nil {
		return nil, tx.Error
	}
	if tx.RowsAffected == 0 {
		return nil, nil
	}
	return &apiToken, nil
}

// GetByBeta gets API tokens by beta key (SDK/bot authorization token).
// Mirrors Python's APIToken.query(beta=token), which returns a list.
func (dao *APITokenDAO) GetByBeta(ctx context.Context, db *gorm.DB, beta string) ([]*entity.APIToken, error) {
	var tokens []*entity.APIToken
	err := db.WithContext(ctx).Where("beta = ?", beta).Find(&tokens).Error
	return tokens, err
}

// DeleteByDialogIDs deletes API tokens by dialog IDs (hard delete)
func (dao *APITokenDAO) DeleteByDialogIDs(ctx context.Context, db *gorm.DB, dialogIDs []string) (int64, error) {
	if len(dialogIDs) == 0 {
		return 0, nil
	}
	result := db.WithContext(ctx).Where("dialog_id IN ?", dialogIDs).Delete(&entity.APIToken{})
	return result.RowsAffected, result.Error
}
```

**Broken control: internal/service/user.go** — `internal/service/user.go:776-795`

Deactivation revokes the stored session identifier but keeps API/beta rows; API identity resolution only requires the session identifier to be nonempty.

```go
func (s *UserService) resolveAPITokenIdentity(ctx context.Context, apiToken *entity.APIToken) (*AuthIdentity, common.ErrorCode, error) {
	if apiToken.UserID == nil || *apiToken.UserID == "" {
		return nil, common.CodeUnauthorized, fmt.Errorf("API token is missing user identity")
	}

	user, err := s.userDAO.GetByID(ctx, dao.DB, *apiToken.UserID)
	if err != nil {
		return nil, common.CodeUnauthorized, fmt.Errorf("user not found for API token")
	}
	if user.AccessToken == nil || *user.AccessToken == "" {
		return nil, common.CodeUnauthorized, fmt.Errorf("user has empty access_token in database")
	}
	tenantID, err := resolveUserAuthTenant(ctx, user, apiToken.TenantID)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	apiTokenMetadata := *apiToken
	apiTokenMetadata.TenantID = tenantID
	return &AuthIdentity{User: user, TenantID: tenantID, APIToken: &apiTokenMetadata}, common.CodeSuccess, nil
```

**Trace: internal/service/stub.go** — `internal/service/stub.go:74-81`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/service/stub.go transition.

```go
	return "", false, nil
}

// resolveUserAuthTenant discards tenant context because community credentials identify only a user.
func resolveUserAuthTenant(_ context.Context, _ *entity.User, _ string) (string, error) {
	return "", nil
}

```

**Trace: internal/handler/auth.go** — `internal/handler/auth.go:172-180`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/handler/auth.go transition.

```go
		identity, code, err := h.userService.ResolveAccessToken(ctx, token)
		if err != nil {
			identity, code, err = h.userService.ResolveAPIToken(ctx, token)
			if err != nil {
				common.Respond(c, http.StatusUnauthorized, code, nil, "Invalid access token")
				c.Abort()
				return
			}
			authViaAPIToken = true
```

**Trace: internal/handler/common.go** — `internal/handler/common.go:79-90`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/handler/common.go transition.

```go
func GetUser(c *gin.Context) (*entity.User, common.ErrorCode, string) {
	userAny, exist := c.Get("user")
	if !exist {
		return nil, common.CodeUnauthorized, "User not found"
	}

	user, ok := userAny.(*entity.User)
	if !ok {
		return nil, common.CodeUnauthorized, "User not found"
	}
	return user, common.CodeSuccess, ""
}
```

#### Validation

An administratively deactivated user can continue authenticating with previously issued API/beta keys because account state is not checked by their identity resolver. Deactivation revokes the stored session identifier but keeps API/beta rows; API identity resolution only requires the session identifier to be nonempty.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Trace: internal/admin/service.go** — `internal/admin/service.go:456-467`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/admin/service.go transition.

```go
	if user.IsActive == targetStatus {
		return nil
	}

	user.IsActive = targetStatus
	if !isActive {
		invalidToken := "INVALID_" + common.GenerateToken()
		user.AccessToken = &invalidToken
	}

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return fmt.Errorf("failed to update user: %w", err)
```

**Trace: internal/dao/api_token.go** — `internal/dao/api_token.go:48-74`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/dao/api_token.go transition.

```go
	var apiToken entity.APIToken
	tx := db.WithContext(ctx).Where("token = ?", token).Find(&apiToken)
	if tx.Error != nil {
		return nil, tx.Error
	}
	if tx.RowsAffected == 0 {
		return nil, nil
	}
	return &apiToken, nil
}

// GetByBeta gets API tokens by beta key (SDK/bot authorization token).
// Mirrors Python's APIToken.query(beta=token), which returns a list.
func (dao *APITokenDAO) GetByBeta(ctx context.Context, db *gorm.DB, beta string) ([]*entity.APIToken, error) {
	var tokens []*entity.APIToken
	err := db.WithContext(ctx).Where("beta = ?", beta).Find(&tokens).Error
	return tokens, err
}

// DeleteByDialogIDs deletes API tokens by dialog IDs (hard delete)
func (dao *APITokenDAO) DeleteByDialogIDs(ctx context.Context, db *gorm.DB, dialogIDs []string) (int64, error) {
	if len(dialogIDs) == 0 {
		return 0, nil
	}
	result := db.WithContext(ctx).Where("dialog_id IN ?", dialogIDs).Delete(&entity.APIToken{})
	return result.RowsAffected, result.Error
}
```

**Broken control: internal/service/user.go** — `internal/service/user.go:776-795`

Deactivation revokes the stored session identifier but keeps API/beta rows; API identity resolution only requires the session identifier to be nonempty.

```go
func (s *UserService) resolveAPITokenIdentity(ctx context.Context, apiToken *entity.APIToken) (*AuthIdentity, common.ErrorCode, error) {
	if apiToken.UserID == nil || *apiToken.UserID == "" {
		return nil, common.CodeUnauthorized, fmt.Errorf("API token is missing user identity")
	}

	user, err := s.userDAO.GetByID(ctx, dao.DB, *apiToken.UserID)
	if err != nil {
		return nil, common.CodeUnauthorized, fmt.Errorf("user not found for API token")
	}
	if user.AccessToken == nil || *user.AccessToken == "" {
		return nil, common.CodeUnauthorized, fmt.Errorf("user has empty access_token in database")
	}
	tenantID, err := resolveUserAuthTenant(ctx, user, apiToken.TenantID)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	apiTokenMetadata := *apiToken
	apiTokenMetadata.TenantID = tenantID
	return &AuthIdentity{User: user, TenantID: tenantID, APIToken: &apiTokenMetadata}, common.CodeSuccess, nil
```

**Trace: internal/service/stub.go** — `internal/service/stub.go:74-81`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/service/stub.go transition.

```go
	return "", false, nil
}

// resolveUserAuthTenant discards tenant context because community credentials identify only a user.
func resolveUserAuthTenant(_ context.Context, _ *entity.User, _ string) (string, error) {
	return "", nil
}

```

**Trace: internal/handler/auth.go** — `internal/handler/auth.go:172-180`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/handler/auth.go transition.

```go
		identity, code, err := h.userService.ResolveAccessToken(ctx, token)
		if err != nil {
			identity, code, err = h.userService.ResolveAPIToken(ctx, token)
			if err != nil {
				common.Respond(c, http.StatusUnauthorized, code, nil, "Invalid access token")
				c.Abort()
				return
			}
			authViaAPIToken = true
```

**Trace: internal/handler/common.go** — `internal/handler/common.go:79-90`

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity. This source segment establishes the internal/handler/common.go transition.

```go
func GetUser(c *gin.Context) (*entity.User, common.ErrorCode, string) {
	userAny, exist := c.Get("user")
	if !exist {
		return nil, common.CodeUnauthorized, "User not found"
	}

	user, ok := userAny.(*entity.User)
	if !ok {
		return nil, common.CodeUnauthorized, "User not found"
	}
	return user, common.CodeSuccess, ""
}
```

Counterevidence and remaining uncertainty:
- New password login checks IsActive and existing session tokens are invalidated. This is not an arbitrary cross-tenant bypass. OSS tenant resolver does not add an active-user check.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

Admin disables user → IsActive=0, AccessToken=INVALID_random → API token lookup → user lookup → nonempty AccessToken passes → resource permissions accept former identity.

**Broken control: internal/service/user.go** — `internal/service/user.go:776-795`

Deactivation revokes the stored session identifier but keeps API/beta rows; API identity resolution only requires the session identifier to be nonempty.

```go
func (s *UserService) resolveAPITokenIdentity(ctx context.Context, apiToken *entity.APIToken) (*AuthIdentity, common.ErrorCode, error) {
	if apiToken.UserID == nil || *apiToken.UserID == "" {
		return nil, common.CodeUnauthorized, fmt.Errorf("API token is missing user identity")
	}

	user, err := s.userDAO.GetByID(ctx, dao.DB, *apiToken.UserID)
	if err != nil {
		return nil, common.CodeUnauthorized, fmt.Errorf("user not found for API token")
	}
	if user.AccessToken == nil || *user.AccessToken == "" {
		return nil, common.CodeUnauthorized, fmt.Errorf("user has empty access_token in database")
	}
	tenantID, err := resolveUserAuthTenant(ctx, user, apiToken.TenantID)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	apiTokenMetadata := *apiToken
	apiTokenMetadata.TenantID = tenantID
	return &AuthIdentity{User: user, TenantID: tenantID, APIToken: &apiTokenMetadata}, common.CodeSuccess, nil
```

#### Reachability

Former user or holder of a previously issued key, with API connectivity. Access is confined to the identity's existing resource permissions.

Existing controls:
- New password login checks IsActive and existing session tokens are invalidated. This is not an arbitrary cross-tenant bypass. OSS tenant resolver does not add an active-user check.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**High** — Direct credential-boundary failure permits private data access through an ordinarily distributed or formerly authorized credential. Former user or holder of a previously issued key, with API connectivity. Access is confined to the identity's existing resource permissions.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Apply a shared active/deleted-account check to all credential resolvers; revoke API and beta credentials on deactivation according to policy. Fail closed before resource access.

Tests:
- Issue session/API/beta credentials, deactivate user, assert all credential classes and standalone MCP fail; test reactivation and intentional reissuance.

<a id="finding-2"></a>

### [2] Public share beta tokens gain the owner's MCP retrieval scope

| Field | Value |
| --- | --- |
| Severity | high |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Authorization scope escalation |
| CWE | CWE-863 |
| Affected lines | web/src/components/embed-dialog/use-show-embed-dialog.ts:44-52, web/src/components/embed-dialog/index.tsx:184-187, internal/service/api_token.go:96-107, internal/handler/auth.go:138-149, internal/router/router.go:219-222, internal/handler/mcp_server.go:99-106, internal/handler/mcp_server.go:67-76, internal/handler/mcp_retrieval.go:62-80 |

#### Summary

A recipient of a public chat/agent link can reuse its auth beta credential at POST /api/v1/mcp. The middleware resolves the owner's user identity and MCP lists/retrieves datasets outside the shared application.

#### Root Cause

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. Beta authentication loses the capability's intended sharing scope and installs the owner identity; MCP accepts it without constraining tools or resources.

**Trace: web/src/components/embed-dialog/use-show-embed-dialog.ts** — `web/src/components/embed-dialog/use-show-embed-dialog.ts:44-52`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the web/src/components/embed-dialog/use-show-embed-dialog.ts transition.

```typescript
  const { data: tokenList, fetchSystemTokenList } =
    useFetchManualSystemTokenList();

  let token = '',
    beta = '';

  if (Array.isArray(tokenList) && tokenList.length > 0) {
    token = tokenList[0].token;
    beta = tokenList[0].beta;
```

**Trace: web/src/components/embed-dialog/index.tsx** — `web/src/components/embed-dialog/index.tsx:184-187`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the web/src/components/embed-dialog/index.tsx transition.

```typescript
    const src = new URL(`${location.origin}${baseRoute}`);
    src.searchParams.append('shared_id', token);
    src.searchParams.append('from', from);
    src.searchParams.append('auth', beta);
```

**Trace: internal/service/api_token.go** — `internal/service/api_token.go:96-107`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/service/api_token.go transition.

```go
	// Generate key and beta values
	// key: "ragflow-" + secrets.token_urlsafe(32)
	APIToken := common.GenerateAPIToken()
	// beta: generate_confirmation_token().replace("ragflow-", "")[:32]
	betaAPIKey := common.GenerateBetaAPIToken()

	APIKeyData := &entity.APIToken{
		TenantID: tenantID,
		UserID:   &userID,
		Token:    APIToken,
		Beta:     &betaAPIKey,
	}
```

**Trace: internal/handler/auth.go** — `internal/handler/auth.go:138-149`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/handler/auth.go transition.

```go
		if identity, code, err := h.userService.ResolveBetaAPIToken(ctx, auth); err == nil && code == common.CodeSuccess {
			if !billingAllowsAPIToken(ctx, identity.TenantID) {
				common.RespondError(c, common.CodePermissionError, "API key requires a Starter or Pro plan")
				c.Abort()
				return
			}
			setAuthIdentity(c, identity)
			c.Set("auth_via_beta_token", true)
			if identity.APIToken != nil && identity.APIToken.DialogID != nil {
				c.Set("agent_id", *identity.APIToken.DialogID)
			}
			c.Next()
```

**Trace: internal/router/router.go** — `internal/router/router.go:219-222`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/router/router.go transition.

```go
		// MCP server endpoint — exposes RAGFlow capabilities as MCP tools.
		// Uses BetaAuthMiddleware to resolve the user from the
		// Authorization header.
		apiBetaAuth.POST("/mcp", r.mcpServerHandler.HandleMCP)
```

**Broken control: internal/handler/mcp_server.go** — `internal/handler/mcp_server.go:99-106`

Beta authentication loses the capability's intended sharing scope and installs the owner identity; MCP accepts it without constraining tools or resources.

```go
func (h *MCPServerHandler) HandleMCP(c *gin.Context) {
	user, errorCode, errorMessage := GetUser(c)
	if errorCode != common.CodeSuccess {
		common.RespondError(c, errorCode, errorMessage)
		return
	}

	hdl := h.newTransport(func(context.Context, string) (string, error) { return user.ID, nil }, mcp.Options{StreamableHTTP: true, JSONResponse: true})
```

**Trace: internal/handler/mcp_server.go** — `internal/handler/mcp_server.go:67-76`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/handler/mcp_server.go transition.

```go
func (h *MCPServerHandler) NewStandalone(ctx context.Context, auth *AuthHandler, cfg config.MCPConfig) (*mcp.Handler, error) {
	resolveUser := func(ctx context.Context, authorization string) (string, error) {
		if cfg.LaunchMode == "self-host" {
			authorization = cfg.HostAPIKey
		}
		user, err := auth.ResolveMCPUser(ctx, authorization)
		if err != nil {
			return "", err
		}
		return user.ID, nil
```

**Trace: internal/handler/mcp_retrieval.go** — `internal/handler/mcp_retrieval.go:62-80`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/handler/mcp_retrieval.go transition.

```go
	// Resolve dataset IDs: if none provided, fetch ALL accessible datasets
	// across all pages (matching Python _fetch_all_datasets behaviour).
	datasetIDs := req.DatasetIDs
	if len(datasetIDs) == 0 {
		const maxPageSize = 100
		ids, err := fetchAllDatasetIDs(func(page, pageSize int) ([]map[string]interface{}, int64, error) {
			data, total, _, err := ds.ListDatasets(ctx,
				"", "", page, pageSize, []dao.OrderTerm{{Column: "create_time", Desc: true}},
				"", nil, "", nil, "",
			)
			return data, total, err
		}, maxPageSize)
		if err != nil {
			return "", fmt.Errorf("cannot resolve accessible datasets: %w", err)
		}
		if len(ids) == 0 {
			return "", fmt.Errorf("No accessible datasets found.")
		}
		datasetIDs = ids
```

#### Validation

A recipient of a public chat/agent link can reuse its auth beta credential at POST /api/v1/mcp. The middleware resolves the owner's user identity and MCP lists/retrieves datasets outside the shared application. Beta authentication loses the capability's intended sharing scope and installs the owner identity; MCP accepts it without constraining tools or resources.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Trace: web/src/components/embed-dialog/use-show-embed-dialog.ts** — `web/src/components/embed-dialog/use-show-embed-dialog.ts:44-52`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the web/src/components/embed-dialog/use-show-embed-dialog.ts transition.

```typescript
  const { data: tokenList, fetchSystemTokenList } =
    useFetchManualSystemTokenList();

  let token = '',
    beta = '';

  if (Array.isArray(tokenList) && tokenList.length > 0) {
    token = tokenList[0].token;
    beta = tokenList[0].beta;
```

**Trace: web/src/components/embed-dialog/index.tsx** — `web/src/components/embed-dialog/index.tsx:184-187`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the web/src/components/embed-dialog/index.tsx transition.

```typescript
    const src = new URL(`${location.origin}${baseRoute}`);
    src.searchParams.append('shared_id', token);
    src.searchParams.append('from', from);
    src.searchParams.append('auth', beta);
```

**Trace: internal/service/api_token.go** — `internal/service/api_token.go:96-107`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/service/api_token.go transition.

```go
	// Generate key and beta values
	// key: "ragflow-" + secrets.token_urlsafe(32)
	APIToken := common.GenerateAPIToken()
	// beta: generate_confirmation_token().replace("ragflow-", "")[:32]
	betaAPIKey := common.GenerateBetaAPIToken()

	APIKeyData := &entity.APIToken{
		TenantID: tenantID,
		UserID:   &userID,
		Token:    APIToken,
		Beta:     &betaAPIKey,
	}
```

**Trace: internal/handler/auth.go** — `internal/handler/auth.go:138-149`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/handler/auth.go transition.

```go
		if identity, code, err := h.userService.ResolveBetaAPIToken(ctx, auth); err == nil && code == common.CodeSuccess {
			if !billingAllowsAPIToken(ctx, identity.TenantID) {
				common.RespondError(c, common.CodePermissionError, "API key requires a Starter or Pro plan")
				c.Abort()
				return
			}
			setAuthIdentity(c, identity)
			c.Set("auth_via_beta_token", true)
			if identity.APIToken != nil && identity.APIToken.DialogID != nil {
				c.Set("agent_id", *identity.APIToken.DialogID)
			}
			c.Next()
```

**Trace: internal/router/router.go** — `internal/router/router.go:219-222`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/router/router.go transition.

```go
		// MCP server endpoint — exposes RAGFlow capabilities as MCP tools.
		// Uses BetaAuthMiddleware to resolve the user from the
		// Authorization header.
		apiBetaAuth.POST("/mcp", r.mcpServerHandler.HandleMCP)
```

**Broken control: internal/handler/mcp_server.go** — `internal/handler/mcp_server.go:99-106`

Beta authentication loses the capability's intended sharing scope and installs the owner identity; MCP accepts it without constraining tools or resources.

```go
func (h *MCPServerHandler) HandleMCP(c *gin.Context) {
	user, errorCode, errorMessage := GetUser(c)
	if errorCode != common.CodeSuccess {
		common.RespondError(c, errorCode, errorMessage)
		return
	}

	hdl := h.newTransport(func(context.Context, string) (string, error) { return user.ID, nil }, mcp.Options{StreamableHTTP: true, JSONResponse: true})
```

**Trace: internal/handler/mcp_server.go** — `internal/handler/mcp_server.go:67-76`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/handler/mcp_server.go transition.

```go
func (h *MCPServerHandler) NewStandalone(ctx context.Context, auth *AuthHandler, cfg config.MCPConfig) (*mcp.Handler, error) {
	resolveUser := func(ctx context.Context, authorization string) (string, error) {
		if cfg.LaunchMode == "self-host" {
			authorization = cfg.HostAPIKey
		}
		user, err := auth.ResolveMCPUser(ctx, authorization)
		if err != nil {
			return "", err
		}
		return user.ID, nil
```

**Trace: internal/handler/mcp_retrieval.go** — `internal/handler/mcp_retrieval.go:62-80`

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval. This source segment establishes the internal/handler/mcp_retrieval.go transition.

```go
	// Resolve dataset IDs: if none provided, fetch ALL accessible datasets
	// across all pages (matching Python _fetch_all_datasets behaviour).
	datasetIDs := req.DatasetIDs
	if len(datasetIDs) == 0 {
		const maxPageSize = 100
		ids, err := fetchAllDatasetIDs(func(page, pageSize int) ([]map[string]interface{}, int64, error) {
			data, total, _, err := ds.ListDatasets(ctx,
				"", "", page, pageSize, []dao.OrderTerm{{Column: "create_time", Desc: true}},
				"", nil, "", nil, "",
			)
			return data, total, err
		}, maxPageSize)
		if err != nil {
			return "", fmt.Errorf("cannot resolve accessible datasets: %w", err)
		}
		if len(ids) == 0 {
			return "", fmt.Errorf("No accessible datasets found.")
		}
		datasetIDs = ids
```

Counterevidence and remaining uncertainty:
- Normal resource permission checks execute, but against the owner. Ordinary protected routes do not accept beta tokens. No exploit executed.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

Embed UI exposes auth=beta → BetaAuthMiddleware → ResolveBetaAPIToken → owner principal → HandleMCP → owner-scoped dataset list/retrieval.

**Broken control: internal/handler/mcp_server.go** — `internal/handler/mcp_server.go:99-106`

Beta authentication loses the capability's intended sharing scope and installs the owner identity; MCP accepts it without constraining tools or resources.

```go
func (h *MCPServerHandler) HandleMCP(c *gin.Context) {
	user, errorCode, errorMessage := GetUser(c)
	if errorCode != common.CodeSuccess {
		common.RespondError(c, errorCode, errorMessage)
		return
	}

	hdl := h.newTransport(func(context.Context, string) (string, error) { return user.ID, nil }, mcp.Options{StreamableHTTP: true, JSONResponse: true})
```

#### Reachability

Anyone holding a valid shared-link beta credential; API MCP must be reachable. RAGFLOW_MCP_ENABLED=false disables only the optional listener, not /api/v1/mcp. Local lab Nginx blocks this route.

Existing controls:
- Normal resource permission checks execute, but against the owner. Ordinary protected routes do not accept beta tokens. No exploit executed.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**High** — Direct credential-boundary failure permits private data access through an ordinarily distributed or formerly authorized credential. Anyone holding a valid shared-link beta credential; API MCP must be reachable. RAGFLOW_MCP_ENABLED=false disables only the optional listener, not /api/v1/mcp. Local lab Nginx blocks this route.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Reject beta credentials at API and standalone MCP; mint separate expiring share capabilities bound to application, resource scope and operations. Verify every beta-enabled route.

Tests:
- Use two synthetic datasets: shared application A and private dataset B. A beta credential must fail MCP initialize/tool calls and never list/retrieve B; owner API key should retain authorized access.

<a id="finding-3"></a>

### [3] Administrative password reset leaves existing sessions valid

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Insufficient session invalidation |
| CWE | CWE-613 |
| Affected lines | internal/admin/service.go:397-429, internal/service/user.go:515-536, internal/service/user.go:680-690, internal/common/token.go:34-48 |

#### Summary

Admin ChangePassword updates the password hash without rotating the stored access-token identifier. A stolen existing session remains valid after the reset until normal expiry or another invalidation event.

#### Root Cause

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. The administrative recovery path does not perform the session revocation applied by the user settings password-change path.

**Broken control: internal/admin/service.go** — `internal/admin/service.go:397-429`

The administrative recovery path does not perform the session revocation applied by the user settings password-change path.

```go
func (s *Service) ChangePassword(ctx context.Context, username, newPassword string) error {
	userList, err := s.userDAO.ListByEmail(ctx, dao.DB, username)
	if err != nil || len(userList) == 0 {
		return fmt.Errorf("user '%s' not found", username)
	}

	if len(userList) > 1 {
		return fmt.Errorf("exist more than 1 user: %s", username)
	}

	user := userList[0]

	decryptedPassword, err := common.DecryptPassword(newPassword)
	if err != nil {
		return fmt.Errorf("failed to decrypt password: %w", err)
	}

	if user.Password != nil && common.CheckWerkzeugPassword(decryptedPassword, *user.Password) {
		return nil
	}

	hashedPassword, err := common.GenerateWerkzeugPasswordHash(decryptedPassword)
	if err != nil {
		return fmt.Errorf("failed to hash password: %w", err)
	}

	user.Password = &hashedPassword

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return fmt.Errorf("failed to update user: %w", err)
	}

	return nil
```

**Trace: internal/service/user.go** — `internal/service/user.go:515-536`

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. This source segment establishes the internal/service/user.go transition.

```go
	tokenContext, err := common.ExtractAccessTokenContext(authorization, secretKey)
	if err != nil {
		return nil, common.CodeUnauthorized, fmt.Errorf("invalid authorization token: %w", err)
	}

	// Validate token format (should be at least 32 chars, UUID format)
	if len(tokenContext.AccessToken) < 32 {
		return nil, common.CodeUnauthorized, fmt.Errorf("invalid access token format")
	}

	// Get user by access token
	user, err := s.userDAO.GetByAccessToken(ctx, dao.DB, tokenContext.AccessToken)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	tenantID, err := resolveUserAuthTenant(ctx, user, tokenContext.TenantID)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	return &AuthIdentity{User: user, TenantID: tenantID}, common.CodeSuccess, nil
```

**Trace: internal/service/user.go** — `internal/service/user.go:680-690`

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. This source segment establishes the internal/service/user.go transition.

```go
			}

			var hashedPassword string
			hashedPassword, err = common.GenerateWerkzeugPasswordHash(string(newPasswordBytes))
			if err != nil {
				return common.CodeExceptionError, err
			}
			user.Password = &hashedPassword
			invalidToken := "INVALID_" + common.GenerateToken()
			user.AccessToken = &invalidToken
		}
```

**Trace: internal/common/token.go** — `internal/common/token.go:34-48`

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. This source segment establishes the internal/common/token.go transition.

```go
const accessTokenExpireSeconds = 86400

const accessTokenContextVersion = "v2"

// AccessTokenContext is the identity and tenant context carried by a signed
// user token. TenantID is empty in Community Edition and for system admins.
type AccessTokenContext struct {
	AccessToken string
	TenantID    string
}

// ExtractAccessTokenContext extracts the access token and tenant context from
// an authorization header.
func ExtractAccessTokenContext(authorization, secretKey string) (*AccessTokenContext, error) {
	if authorization == "" {
```

#### Validation

Admin ChangePassword updates the password hash without rotating the stored access-token identifier. A stolen existing session remains valid after the reset until normal expiry or another invalidation event. The administrative recovery path does not perform the session revocation applied by the user settings password-change path.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Broken control: internal/admin/service.go** — `internal/admin/service.go:397-429`

The administrative recovery path does not perform the session revocation applied by the user settings password-change path.

```go
func (s *Service) ChangePassword(ctx context.Context, username, newPassword string) error {
	userList, err := s.userDAO.ListByEmail(ctx, dao.DB, username)
	if err != nil || len(userList) == 0 {
		return fmt.Errorf("user '%s' not found", username)
	}

	if len(userList) > 1 {
		return fmt.Errorf("exist more than 1 user: %s", username)
	}

	user := userList[0]

	decryptedPassword, err := common.DecryptPassword(newPassword)
	if err != nil {
		return fmt.Errorf("failed to decrypt password: %w", err)
	}

	if user.Password != nil && common.CheckWerkzeugPassword(decryptedPassword, *user.Password) {
		return nil
	}

	hashedPassword, err := common.GenerateWerkzeugPasswordHash(decryptedPassword)
	if err != nil {
		return fmt.Errorf("failed to hash password: %w", err)
	}

	user.Password = &hashedPassword

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return fmt.Errorf("failed to update user: %w", err)
	}

	return nil
```

**Trace: internal/service/user.go** — `internal/service/user.go:515-536`

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. This source segment establishes the internal/service/user.go transition.

```go
	tokenContext, err := common.ExtractAccessTokenContext(authorization, secretKey)
	if err != nil {
		return nil, common.CodeUnauthorized, fmt.Errorf("invalid authorization token: %w", err)
	}

	// Validate token format (should be at least 32 chars, UUID format)
	if len(tokenContext.AccessToken) < 32 {
		return nil, common.CodeUnauthorized, fmt.Errorf("invalid access token format")
	}

	// Get user by access token
	user, err := s.userDAO.GetByAccessToken(ctx, dao.DB, tokenContext.AccessToken)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	tenantID, err := resolveUserAuthTenant(ctx, user, tokenContext.TenantID)
	if err != nil {
		return nil, common.CodeUnauthorized, err
	}

	return &AuthIdentity{User: user, TenantID: tenantID}, common.CodeSuccess, nil
```

**Trace: internal/service/user.go** — `internal/service/user.go:680-690`

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. This source segment establishes the internal/service/user.go transition.

```go
			}

			var hashedPassword string
			hashedPassword, err = common.GenerateWerkzeugPasswordHash(string(newPasswordBytes))
			if err != nil {
				return common.CodeExceptionError, err
			}
			user.Password = &hashedPassword
			invalidToken := "INVALID_" + common.GenerateToken()
			user.AccessToken = &invalidToken
		}
```

**Trace: internal/common/token.go** — `internal/common/token.go:34-48`

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted. This source segment establishes the internal/common/token.go transition.

```go
const accessTokenExpireSeconds = 86400

const accessTokenContextVersion = "v2"

// AccessTokenContext is the identity and tenant context carried by a signed
// user token. TenantID is empty in Community Edition and for system admins.
type AccessTokenContext struct {
	AccessToken string
	TenantID    string
}

// ExtractAccessTokenContext extracts the access token and tenant context from
// an authorization header.
func ExtractAccessTokenContext(authorization, secretKey string) (*AccessTokenContext, error) {
	if authorization == "" {
```

Counterevidence and remaining uncertainty:
- Self-service password updates rotate AccessToken; session signatures and 24-hour expiration still work. API key lifecycle is a separate policy.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

Admin password reset → user.Password updated → user record saved with original AccessToken → ResolveAccessToken finds same identifier → old signed session accepted.

**Broken control: internal/admin/service.go** — `internal/admin/service.go:397-429`

The administrative recovery path does not perform the session revocation applied by the user settings password-change path.

```go
func (s *Service) ChangePassword(ctx context.Context, username, newPassword string) error {
	userList, err := s.userDAO.ListByEmail(ctx, dao.DB, username)
	if err != nil || len(userList) == 0 {
		return fmt.Errorf("user '%s' not found", username)
	}

	if len(userList) > 1 {
		return fmt.Errorf("exist more than 1 user: %s", username)
	}

	user := userList[0]

	decryptedPassword, err := common.DecryptPassword(newPassword)
	if err != nil {
		return fmt.Errorf("failed to decrypt password: %w", err)
	}

	if user.Password != nil && common.CheckWerkzeugPassword(decryptedPassword, *user.Password) {
		return nil
	}

	hashedPassword, err := common.GenerateWerkzeugPasswordHash(decryptedPassword)
	if err != nil {
		return fmt.Errorf("failed to hash password: %w", err)
	}

	user.Password = &hashedPassword

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return fmt.Errorf("failed to update user: %w", err)
	}

	return nil
```

#### Reachability

Attacker already has a valid session when administrator resets the password; window is bounded by the session's 24-hour expiry, login/logout or explicit token rotation.

Existing controls:
- Self-service password updates rotate AccessToken; session signatures and 24-hour expiration still work. API key lifecycle is a separate policy.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**Medium** — High confidentiality/authority impact is conditional on the stated configuration, existing credential or network position. Attacker already has a valid session when administrator resets the password; window is bounded by the session's 24-hour expiry, login/logout or explicit token rotation.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Rotate AccessToken or increment an authentication epoch atomically with administrative password reset; invalidate corresponding sessions and define separate API-key recovery policy.

Tests:
- Capture synthetic user session, reset through admin API, require old session failure; ensure fresh login with new password works.

<a id="finding-4"></a>

### [4] Disabling password login does not block password authentication

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Authentication policy enforcement bypass |
| CWE | CWE-863 |
| Affected lines | internal/server/config/api_server_config.go:95-121, internal/service/system.go:43-54, internal/router/router.go:167-171, internal/handler/user.go:236-245, internal/service/user.go:308-341 |

#### Summary

DISABLE_PASSWORD_LOGIN=true or authentication.disable_password_login=true changes exposed configuration, but direct POST /api/v1/auth/login still verifies a password and issues a session.

#### Root Cause

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. The password login entrypoint never checks the parsed DisablePasswordLogin policy.

**Trace: internal/server/config/api_server_config.go** — `internal/server/config/api_server_config.go:95-121`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/server/config/api_server_config.go transition.

```go
func (c *Config) parseAuthenticationConfig(v *viper.Viper) {
	apiServerConfig := &c.apiServer
	apiServerConfig.Authentication.DisablePasswordLogin = false
	apiServerConfig.Authentication.EnableRegister = true

	if !v.IsSet("authentication") {
		return
	}
	sub := v.Sub("authentication")
	if sub == nil {
		return
	}

	if sub.IsSet("disable_password_login") {
		apiServerConfig.Authentication.DisablePasswordLogin = sub.GetBool("disable_password_login")
	}

	if sub.IsSet("enable_register") {
		apiServerConfig.Authentication.EnableRegister = sub.GetBool("enable_register")
	}
}

func (c *Config) DisablePasswordLogin() bool {
	if c.environments.DisablePasswordLogin != nil {
		return *c.environments.DisablePasswordLogin
	}
	return c.apiServer.Authentication.DisablePasswordLogin
```

**Trace: internal/service/system.go** — `internal/service/system.go:43-54`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/service/system.go transition.

```go
type ConfigResponse struct {
	EnableRegister       bool `json:"registerEnabled"`
	DisablePasswordLogin bool `json:"disablePasswordLogin"`
}

// GetConfig get system configuration
func (s *SystemService) GetConfig() (*ConfigResponse, error) {
	cfg := server.GetConfig()
	return &ConfigResponse{
		EnableRegister:       cfg.EnableRegister(),
		DisablePasswordLogin: cfg.DisablePasswordLogin(),
	}, nil
```

**Trace: internal/router/router.go** — `internal/router/router.go:167-171`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/router/router.go transition.

```go
		// User login by email endpoint
		apiNoAuth.POST("/auth/login", r.userHandler.LoginByEmail)

		// Register
		apiNoAuth.POST("/users", r.userHandler.Register)
```

**Trace: internal/handler/user.go** — `internal/handler/user.go:236-245`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/handler/user.go transition.

```go
	if !local.IsAdminAvailable() {
		adminStatus := local.GetAdminStatus()
		common.RespondError(c, common.CodeAuthenticationError, adminStatus.Reason)
		operationLog.Code = int(common.CodeAuthenticationError)
		operationLog.Error = errors.New(adminStatus.Reason)
		return
	}

	user, code, err := h.userService.LoginByEmail(ctx, &req)
	if err != nil {
```

**Broken control: internal/service/user.go** — `internal/service/user.go:308-341`

The password login entrypoint never checks the parsed DisablePasswordLogin policy.

```go
func (s *UserService) LoginByEmail(ctx context.Context, req *EmailLoginRequest) (*entity.User, common.ErrorCode, error) {
	user, err := s.userDAO.GetByEmail(ctx, dao.DB, req.Email)
	if err != nil {
		common.Error("user not found by email", err)
		return nil, common.CodeAuthenticationError, fmt.Errorf("email: %s is not registered", req.Email)
	}

	decryptedPassword, err := common.DecryptPassword(req.Password)
	if err != nil {
		return nil, common.CodeServerError, fmt.Errorf("fail to crypt password")
	}

	if user.Password == nil || !s.VerifyPassword(*user.Password, decryptedPassword) {
		return nil, common.CodeAuthenticationError, fmt.Errorf("email and password do not match")
	}

	if user.IsActive == "0" {
		return nil, common.CodeForbidden, fmt.Errorf("this account has been disabled, please contact the administrator")
	}

	// Generate new access token
	token := common.GenerateToken()
	user.AccessToken = &token
	now := time.Now().Truncate(time.Second)
	user.LastLoginTime = &now

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return nil, common.CodeServerError, fmt.Errorf("failed to update user: %w", err)
	}
	if billingService := billing.Get(); billingService != nil && billingService.Enabled() {
		billingService.SyncLoginTokenRateLimit(ctx, user.ID, token)
	}

	return user, common.CodeSuccess, nil
```

#### Validation

DISABLE_PASSWORD_LOGIN=true or authentication.disable_password_login=true changes exposed configuration, but direct POST /api/v1/auth/login still verifies a password and issues a session. The password login entrypoint never checks the parsed DisablePasswordLogin policy.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Trace: internal/server/config/api_server_config.go** — `internal/server/config/api_server_config.go:95-121`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/server/config/api_server_config.go transition.

```go
func (c *Config) parseAuthenticationConfig(v *viper.Viper) {
	apiServerConfig := &c.apiServer
	apiServerConfig.Authentication.DisablePasswordLogin = false
	apiServerConfig.Authentication.EnableRegister = true

	if !v.IsSet("authentication") {
		return
	}
	sub := v.Sub("authentication")
	if sub == nil {
		return
	}

	if sub.IsSet("disable_password_login") {
		apiServerConfig.Authentication.DisablePasswordLogin = sub.GetBool("disable_password_login")
	}

	if sub.IsSet("enable_register") {
		apiServerConfig.Authentication.EnableRegister = sub.GetBool("enable_register")
	}
}

func (c *Config) DisablePasswordLogin() bool {
	if c.environments.DisablePasswordLogin != nil {
		return *c.environments.DisablePasswordLogin
	}
	return c.apiServer.Authentication.DisablePasswordLogin
```

**Trace: internal/service/system.go** — `internal/service/system.go:43-54`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/service/system.go transition.

```go
type ConfigResponse struct {
	EnableRegister       bool `json:"registerEnabled"`
	DisablePasswordLogin bool `json:"disablePasswordLogin"`
}

// GetConfig get system configuration
func (s *SystemService) GetConfig() (*ConfigResponse, error) {
	cfg := server.GetConfig()
	return &ConfigResponse{
		EnableRegister:       cfg.EnableRegister(),
		DisablePasswordLogin: cfg.DisablePasswordLogin(),
	}, nil
```

**Trace: internal/router/router.go** — `internal/router/router.go:167-171`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/router/router.go transition.

```go
		// User login by email endpoint
		apiNoAuth.POST("/auth/login", r.userHandler.LoginByEmail)

		// Register
		apiNoAuth.POST("/users", r.userHandler.Register)
```

**Trace: internal/handler/user.go** — `internal/handler/user.go:236-245`

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config. This source segment establishes the internal/handler/user.go transition.

```go
	if !local.IsAdminAvailable() {
		adminStatus := local.GetAdminStatus()
		common.RespondError(c, common.CodeAuthenticationError, adminStatus.Reason)
		operationLog.Code = int(common.CodeAuthenticationError)
		operationLog.Error = errors.New(adminStatus.Reason)
		return
	}

	user, code, err := h.userService.LoginByEmail(ctx, &req)
	if err != nil {
```

**Broken control: internal/service/user.go** — `internal/service/user.go:308-341`

The password login entrypoint never checks the parsed DisablePasswordLogin policy.

```go
func (s *UserService) LoginByEmail(ctx context.Context, req *EmailLoginRequest) (*entity.User, common.ErrorCode, error) {
	user, err := s.userDAO.GetByEmail(ctx, dao.DB, req.Email)
	if err != nil {
		common.Error("user not found by email", err)
		return nil, common.CodeAuthenticationError, fmt.Errorf("email: %s is not registered", req.Email)
	}

	decryptedPassword, err := common.DecryptPassword(req.Password)
	if err != nil {
		return nil, common.CodeServerError, fmt.Errorf("fail to crypt password")
	}

	if user.Password == nil || !s.VerifyPassword(*user.Password, decryptedPassword) {
		return nil, common.CodeAuthenticationError, fmt.Errorf("email and password do not match")
	}

	if user.IsActive == "0" {
		return nil, common.CodeForbidden, fmt.Errorf("this account has been disabled, please contact the administrator")
	}

	// Generate new access token
	token := common.GenerateToken()
	user.AccessToken = &token
	now := time.Now().Truncate(time.Second)
	user.LastLoginTime = &now

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return nil, common.CodeServerError, fmt.Errorf("failed to update user: %w", err)
	}
	if billingService := billing.Get(); billingService != nil && billingService.Enabled() {
		billingService.SyncLoginTokenRateLimit(ctx, user.ID, token)
	}

	return user, common.CodeSuccess, nil
```

Counterevidence and remaining uncertainty:
- The setting defaults false. Password verification and disabled-user rejection still work; externally enforced gateway restrictions can mitigate reachability.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

Public login route → UserHandler.LoginByEmail → UserService.LoginByEmail → password verification and new access token; config getter is only surfaced in system config.

**Broken control: internal/service/user.go** — `internal/service/user.go:308-341`

The password login entrypoint never checks the parsed DisablePasswordLogin policy.

```go
func (s *UserService) LoginByEmail(ctx context.Context, req *EmailLoginRequest) (*entity.User, common.ErrorCode, error) {
	user, err := s.userDAO.GetByEmail(ctx, dao.DB, req.Email)
	if err != nil {
		common.Error("user not found by email", err)
		return nil, common.CodeAuthenticationError, fmt.Errorf("email: %s is not registered", req.Email)
	}

	decryptedPassword, err := common.DecryptPassword(req.Password)
	if err != nil {
		return nil, common.CodeServerError, fmt.Errorf("fail to crypt password")
	}

	if user.Password == nil || !s.VerifyPassword(*user.Password, decryptedPassword) {
		return nil, common.CodeAuthenticationError, fmt.Errorf("email and password do not match")
	}

	if user.IsActive == "0" {
		return nil, common.CodeForbidden, fmt.Errorf("this account has been disabled, please contact the administrator")
	}

	// Generate new access token
	token := common.GenerateToken()
	user.AccessToken = &token
	now := time.Now().Truncate(time.Second)
	user.LastLoginTime = &now

	if err = s.userDAO.Update(ctx, dao.DB, user); err != nil {
		return nil, common.CodeServerError, fmt.Errorf("failed to update user: %w", err)
	}
	if billingService := billing.Get(); billingService != nil && billingService.Enabled() {
		billingService.SyncLoginTokenRateLimit(ctx, user.ID, token)
	}

	return user, common.CodeSuccess, nil
```

#### Reachability

Caller with a valid password when operator intends to disable this method; no credential-free login is claimed. OSS has no built-in OAuth login implementation.

Existing controls:
- The setting defaults false. Password verification and disabled-user rejection still work; externally enforced gateway restrictions can mitigate reachability.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**Medium** — High confidentiality/authority impact is conditional on the stated configuration, existing credential or network position. Caller with a valid password when operator intends to disable this method; no credential-free login is claimed. OSS has no built-in OAuth login implementation.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Reject password authentication server-side before credential processing when disabled. Keep a separate documented admin break-glass policy and validate usable alternate identity flow.

Tests:
- Set policy through YAML and env, submit valid password directly, require rejection; test normal allowed policy and explicit administrator recovery path.

<a id="finding-5"></a>

### [5] API and Admin listeners ignore configured bind hosts

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Unintended network exposure |
| CWE | CWE-668 |
| Affected lines | internal/server/config/api_server_config.go:71-79, internal/server/config/admin_config.go:38-46, internal/server/api/server.go:376-399, internal/server/admin/server.go:85-90, internal/server/admin/server.go:109-113 |

#### Summary

Setting api.host or admin.host to loopback does not restrict either listener: both build ':port' addresses and listen on available interfaces.

#### Root Cause

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. Listener construction consumes HTTPPort while dropping the parsed Host field.

**Trace: internal/server/config/api_server_config.go** — `internal/server/config/api_server_config.go:71-79`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/config/api_server_config.go transition.

```go
	c.apiServer.Host = "localhost"
	c.apiServer.HTTPPort = 9380

	if v.IsSet("api.host") {
		c.apiServer.Host = v.GetString("api.host")
	}

	if v.IsSet("api.http_port") {
		c.apiServer.HTTPPort = v.GetInt("api.http_port")
```

**Trace: internal/server/config/admin_config.go** — `internal/server/config/admin_config.go:38-46`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/config/admin_config.go transition.

```go
	c.admin.Host = "localhost"
	c.admin.HTTPPort = 9381

	if v.IsSet("admin.host") {
		c.admin.Host = v.GetString("admin.host")
	}

	if v.IsSet("admin.http_port") {
		c.admin.HTTPPort = v.GetInt("admin.http_port")
```

**Broken control: internal/server/api/server.go** — `internal/server/api/server.go:376-399`

Listener construction consumes HTTPPort while dropping the parsed Host field.

```go
	apiServerConfig := globalConfig.GetAPIServerConfig()

	// Create HTTP server with timeouts to prevent slow clients from blocking shutdown
	addr := fmt.Sprintf(":%d", apiServerConfig.HTTPPort)
	srv := &http.Server{
		Addr:              addr,
		Handler:           ginEngine,
		BaseContext:       func(net.Listener) context.Context { return ctx },
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       60 * time.Second,
		// WriteTimeout spans "request header read → response written", so it is a
		// ceiling on the WHOLE request, not on a slow client's reads. Measured
		// (2026-09-15, FRAMES 20q): three multi-hop questions take 150–225s to reach
		// their response, and at 120s the server closed the connection with no
		// response at all — the client reports
		// `RemoteDisconnected('Remote end closed connection without response')` and
		// the benchmark re-runs the whole question (max_retries: 2), so one slow
		// question cost three full pipelines. 180s clears the measured distribution's
		// middle; questions whose composition alone runs past it still need streaming
		// or a larger budget.
		WriteTimeout: 180 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	apiListener, err := net.Listen("tcp", addr)
```

**Trace: internal/server/admin/server.go** — `internal/server/admin/server.go:85-90`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/admin/server.go transition.

```go
	adminConfig := globalConfig.GetAdminServerConfig()
	addr := fmt.Sprintf(":%d", adminConfig.HTTPPort)
	srv := &http.Server{
		Addr:    addr,
		Handler: ginEngine,
	}
```

**Trace: internal/server/admin/server.go** — `internal/server/admin/server.go:109-113`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/admin/server.go transition.

```go
	// Start HTTP server in a goroutine
	go func() {
		common.Info(fmt.Sprintf("Starting RAGFlow admin HTTP server on port: %d", adminConfig.HTTPPort))
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			common.Fatal("Failed to start server", zap.Error(err))
```

#### Validation

Setting api.host or admin.host to loopback does not restrict either listener: both build ':port' addresses and listen on available interfaces. Listener construction consumes HTTPPort while dropping the parsed Host field.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Trace: internal/server/config/api_server_config.go** — `internal/server/config/api_server_config.go:71-79`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/config/api_server_config.go transition.

```go
	c.apiServer.Host = "localhost"
	c.apiServer.HTTPPort = 9380

	if v.IsSet("api.host") {
		c.apiServer.Host = v.GetString("api.host")
	}

	if v.IsSet("api.http_port") {
		c.apiServer.HTTPPort = v.GetInt("api.http_port")
```

**Trace: internal/server/config/admin_config.go** — `internal/server/config/admin_config.go:38-46`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/config/admin_config.go transition.

```go
	c.admin.Host = "localhost"
	c.admin.HTTPPort = 9381

	if v.IsSet("admin.host") {
		c.admin.Host = v.GetString("admin.host")
	}

	if v.IsSet("admin.http_port") {
		c.admin.HTTPPort = v.GetInt("admin.http_port")
```

**Broken control: internal/server/api/server.go** — `internal/server/api/server.go:376-399`

Listener construction consumes HTTPPort while dropping the parsed Host field.

```go
	apiServerConfig := globalConfig.GetAPIServerConfig()

	// Create HTTP server with timeouts to prevent slow clients from blocking shutdown
	addr := fmt.Sprintf(":%d", apiServerConfig.HTTPPort)
	srv := &http.Server{
		Addr:              addr,
		Handler:           ginEngine,
		BaseContext:       func(net.Listener) context.Context { return ctx },
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       60 * time.Second,
		// WriteTimeout spans "request header read → response written", so it is a
		// ceiling on the WHOLE request, not on a slow client's reads. Measured
		// (2026-09-15, FRAMES 20q): three multi-hop questions take 150–225s to reach
		// their response, and at 120s the server closed the connection with no
		// response at all — the client reports
		// `RemoteDisconnected('Remote end closed connection without response')` and
		// the benchmark re-runs the whole question (max_retries: 2), so one slow
		// question cost three full pipelines. 180s clears the measured distribution's
		// middle; questions whose composition alone runs past it still need streaming
		// or a larger budget.
		WriteTimeout: 180 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	apiListener, err := net.Listen("tcp", addr)
```

**Trace: internal/server/admin/server.go** — `internal/server/admin/server.go:85-90`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/admin/server.go transition.

```go
	adminConfig := globalConfig.GetAdminServerConfig()
	addr := fmt.Sprintf(":%d", adminConfig.HTTPPort)
	srv := &http.Server{
		Addr:    addr,
		Handler: ginEngine,
	}
```

**Trace: internal/server/admin/server.go** — `internal/server/admin/server.go:109-113`

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener. This source segment establishes the internal/server/admin/server.go transition.

```go
	// Start HTTP server in a goroutine
	go func() {
		common.Info(fmt.Sprintf("Starting RAGFlow admin HTTP server on port: %d", adminConfig.HTTPPort))
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			common.Fatal("Failed to start server", zap.Error(err))
```

Counterevidence and remaining uncertainty:
- Local lab publishes only 127.0.0.1:18080 and no raw 9380/9381 ports. Listener exposure does not itself bypass application authentication.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

api.host/admin.host parsed → server config → fmt.Sprintf(:port) → net.Listen/ListenAndServe wildcard listener.

**Broken control: internal/server/api/server.go** — `internal/server/api/server.go:376-399`

Listener construction consumes HTTPPort while dropping the parsed Host field.

```go
	apiServerConfig := globalConfig.GetAPIServerConfig()

	// Create HTTP server with timeouts to prevent slow clients from blocking shutdown
	addr := fmt.Sprintf(":%d", apiServerConfig.HTTPPort)
	srv := &http.Server{
		Addr:              addr,
		Handler:           ginEngine,
		BaseContext:       func(net.Listener) context.Context { return ctx },
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       60 * time.Second,
		// WriteTimeout spans "request header read → response written", so it is a
		// ceiling on the WHOLE request, not on a slow client's reads. Measured
		// (2026-09-15, FRAMES 20q): three multi-hop questions take 150–225s to reach
		// their response, and at 120s the server closed the connection with no
		// response at all — the client reports
		// `RemoteDisconnected('Remote end closed connection without response')` and
		// the benchmark re-runs the whole question (max_retries: 2), so one slow
		// question cost three full pipelines. 180s clears the measured distribution's
		// middle; questions whose composition alone runs past it still need streaming
		// or a larger budget.
		WriteTimeout: 180 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	apiListener, err := net.Listen("tcp", addr)
```

#### Reachability

Network peer able to reach the host or shared container network, when operator relied on host binding for isolation. Host firewall, container port mappings and network policy remain effective.

Existing controls:
- Local lab publishes only 127.0.0.1:18080 and no raw 9380/9381 ports. Listener exposure does not itself bypass application authentication.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**Medium** — High confidentiality/authority impact is conditional on the stated configuration, existing credential or network position. Network peer able to reach the host or shared container network, when operator relied on host binding for isolation. Host firewall, container port mappings and network policy remain effective.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Build both addresses with net.JoinHostPort(config.Host, port); test IPv4/IPv6 loopback. Until fixed enforce host firewall, dedicated container networks and remove direct published API/Admin ports.

Tests:
- Configure each service on loopback; inspect actual listeners and verify another host/container cannot connect while intended proxy can.

<a id="finding-6"></a>

### [6] MinIO HTTPS defaults to disabled certificate verification

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Unsafe TLS verification default |
| CWE | CWE-295 |
| Affected lines | docker/service_conf.yaml.template:45-48, internal/server/config/storage_engine_config.go:77-86, internal/server/config/storage_engine_config.go:116-122, internal/storage/minio.go:57-68 |

#### Summary

Setting minio.secure=true without an explicit minio.verify leaves Verify=false; the transport then sets InsecureSkipVerify=true, contrary to the template's documented verification default.

#### Root Cause

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. The parser initializes Verify=false; enabling TLS does not change that default, and the transport directly negates Verify.

**Trace: docker/service_conf.yaml.template** — `docker/service_conf.yaml.template:45-48`

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. This source segment establishes the docker/service_conf.yaml.template transition.

```yaml
  # optional: set to true for HTTPS (SSL/TLS). Used by MinIO client and health check.
  # secure: ${MINIO_SECURE:-false}
  # optional: set to false to allow self-signed certificates (e.g. in development).
  # verify: ${MINIO_VERIFY:-true}
```

**Broken control: internal/server/config/storage_engine_config.go** — `internal/server/config/storage_engine_config.go:77-86`

The parser initializes Verify=false; enabling TLS does not change that default, and the transport directly negates Verify.

```go
func (c *Config) parseMinioConfig(v *viper.Viper) {
	// Default MinIO config
	c.storageEngine.Minio.Host = "localhost:23817"
	c.storageEngine.Minio.User = "rag_flow"
	c.storageEngine.Minio.Password = "infini_rag_flow"
	c.storageEngine.Minio.Bucket = ""
	c.storageEngine.Minio.PrefixPath = ""
	c.storageEngine.Minio.Secure = false
	c.storageEngine.Minio.Verify = false
	c.storageEngine.Minio.Region = ""
```

**Trace: internal/server/config/storage_engine_config.go** — `internal/server/config/storage_engine_config.go:116-122`

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. This source segment establishes the internal/server/config/storage_engine_config.go transition.

```go
	if sub.IsSet("secure") {
		c.storageEngine.Minio.Secure = sub.GetBool("secure")
	}

	if sub.IsSet("verify") {
		c.storageEngine.Minio.Verify = sub.GetBool("verify")
	}
```

**Trace: internal/storage/minio.go** — `internal/storage/minio.go:57-68`

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. This source segment establishes the internal/storage/minio.go transition.

```go
func newMinioTransport(cfg config.MinioConfig) (*http.Transport, error) {
	transport, err := minio.DefaultTransport(cfg.Secure)
	if err != nil {
		return nil, fmt.Errorf("failed to create default transport: %w", err)
	}

	if cfg.Secure {
		if transport.TLSClientConfig == nil {
			transport.TLSClientConfig = &tls.Config{}
		}
		transport.TLSClientConfig.InsecureSkipVerify = !cfg.Verify
	}
```

#### Validation

Setting minio.secure=true without an explicit minio.verify leaves Verify=false; the transport then sets InsecureSkipVerify=true, contrary to the template's documented verification default. The parser initializes Verify=false; enabling TLS does not change that default, and the transport directly negates Verify.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Trace: docker/service_conf.yaml.template** — `docker/service_conf.yaml.template:45-48`

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. This source segment establishes the docker/service_conf.yaml.template transition.

```yaml
  # optional: set to true for HTTPS (SSL/TLS). Used by MinIO client and health check.
  # secure: ${MINIO_SECURE:-false}
  # optional: set to false to allow self-signed certificates (e.g. in development).
  # verify: ${MINIO_VERIFY:-true}
```

**Broken control: internal/server/config/storage_engine_config.go** — `internal/server/config/storage_engine_config.go:77-86`

The parser initializes Verify=false; enabling TLS does not change that default, and the transport directly negates Verify.

```go
func (c *Config) parseMinioConfig(v *viper.Viper) {
	// Default MinIO config
	c.storageEngine.Minio.Host = "localhost:23817"
	c.storageEngine.Minio.User = "rag_flow"
	c.storageEngine.Minio.Password = "infini_rag_flow"
	c.storageEngine.Minio.Bucket = ""
	c.storageEngine.Minio.PrefixPath = ""
	c.storageEngine.Minio.Secure = false
	c.storageEngine.Minio.Verify = false
	c.storageEngine.Minio.Region = ""
```

**Trace: internal/server/config/storage_engine_config.go** — `internal/server/config/storage_engine_config.go:116-122`

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. This source segment establishes the internal/server/config/storage_engine_config.go transition.

```go
	if sub.IsSet("secure") {
		c.storageEngine.Minio.Secure = sub.GetBool("secure")
	}

	if sub.IsSet("verify") {
		c.storageEngine.Minio.Verify = sub.GetBool("verify")
	}
```

**Trace: internal/storage/minio.go** — `internal/storage/minio.go:57-68`

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server. This source segment establishes the internal/storage/minio.go transition.

```go
func newMinioTransport(cfg config.MinioConfig) (*http.Transport, error) {
	transport, err := minio.DefaultTransport(cfg.Secure)
	if err != nil {
		return nil, fmt.Errorf("failed to create default transport: %w", err)
	}

	if cfg.Secure {
		if transport.TLSClientConfig == nil {
			transport.TLSClientConfig = &tls.Config{}
		}
		transport.TLSClientConfig.InsecureSkipVerify = !cfg.Verify
	}
```

Counterevidence and remaining uncertainty:
- Explicit minio.verify:true enables verification and mitigates this issue. Default secure:false does not perform TLS at all.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

minio.secure=true, verify omitted → parseMinioConfig Verify=false → newMinioTransport InsecureSkipVerify=true → object storage request trusts impersonated server.

**Broken control: internal/server/config/storage_engine_config.go** — `internal/server/config/storage_engine_config.go:77-86`

The parser initializes Verify=false; enabling TLS does not change that default, and the transport directly negates Verify.

```go
func (c *Config) parseMinioConfig(v *viper.Viper) {
	// Default MinIO config
	c.storageEngine.Minio.Host = "localhost:23817"
	c.storageEngine.Minio.User = "rag_flow"
	c.storageEngine.Minio.Password = "infini_rag_flow"
	c.storageEngine.Minio.Bucket = ""
	c.storageEngine.Minio.PrefixPath = ""
	c.storageEngine.Minio.Secure = false
	c.storageEngine.Minio.Verify = false
	c.storageEngine.Minio.Region = ""
```

#### Reachability

On-path attacker when HTTPS is enabled and verify omitted or false. The lab explicitly sets verify:true, so this unsafe default is not active there; its secure:false still means plaintext traffic.

Existing controls:
- Explicit minio.verify:true enables verification and mitigates this issue. Default secure:false does not perform TLS at all.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**Medium** — High confidentiality/authority impact is conditional on the stated configuration, existing credential or network position. On-path attacker when HTTPS is enabled and verify omitted or false. The lab explicitly sets verify:true, so this unsafe default is not active there; its secure:false still means plaintext traffic.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Set minio.secure:true and minio.verify:true explicitly with trusted CA. Change parser default to true and test omitted verification, keeping insecure opt-out restricted to development.

Tests:
- With secure=true and verify omitted reject self-signed/wrong-host certificates; explicit approved CA succeeds. Confirm lab/production effective config.

<a id="finding-7"></a>

### [7] Elasticsearch HTTPS client skips certificate verification

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Current source shows the complete relevant control path; parent reviewed input, state transition, consumer and counterevidence. Runtime reproduction and image equivalence were not tested. |
| Category | Improper certificate validation |
| CWE | CWE-295 |
| Affected lines | internal/server/config/doc_engine_config.go:53-58, internal/engine/elasticsearch/client.go:43-58 |

#### Summary

When es.hosts uses HTTPS, the Go Elasticsearch transport unconditionally sets InsecureSkipVerify=true, accepting an untrusted or wrong-host certificate.

#### Root Cause

Configured es.hosts and credentials → NewEngine → TLS transport with verification disabled → index/query requests and Basic credentials sent to impersonated endpoint. Certificate chain and hostname verification are disabled in the shared ES transport, with no verification/CA field in ElasticsearchConfig.

**Trace: internal/server/config/doc_engine_config.go** — `internal/server/config/doc_engine_config.go:53-58`

Configured es.hosts and credentials → NewEngine → TLS transport with verification disabled → index/query requests and Basic credentials sent to impersonated endpoint. This source segment establishes the internal/server/config/doc_engine_config.go transition.

```go
// ElasticsearchConfig Elasticsearch configuration
type ElasticsearchConfig struct {
	Hosts    string `mapstructure:"hosts"`
	Username string `mapstructure:"username"`
	Password string `mapstructure:"password"`
}
```

**Broken control: internal/engine/elasticsearch/client.go** — `internal/engine/elasticsearch/client.go:43-58`

Certificate chain and hostname verification are disabled in the shared ES transport, with no verification/CA field in ElasticsearchConfig.

```go
func NewEngine(ctx context.Context, esConfig config.ElasticsearchConfig) (*Engine, error) {
	// Create ES client
	client, err := elasticsearch.NewClient(elasticsearch.Config{
		Addresses: []string{esConfig.Hosts},
		Username:  esConfig.Username,
		Password:  esConfig.Password,
		Transport: &http.Transport{
			MaxIdleConns:          1000,
			MaxIdleConnsPerHost:   300,
			MaxConnsPerHost:       500,
			IdleConnTimeout:       60 * time.Second,
			ResponseHeaderTimeout: 30 * time.Second,
			TLSClientConfig:       &tls.Config{InsecureSkipVerify: true},
			ForceAttemptHTTP2:     true,
		},
	})
```

#### Validation

When es.hosts uses HTTPS, the Go Elasticsearch transport unconditionally sets InsecureSkipVerify=true, accepting an untrusted or wrong-host certificate. Certificate chain and hostname verification are disabled in the shared ES transport, with no verification/CA field in ElasticsearchConfig.

Validation method: Read-only static source inspection; independent investigator results checked against current source by parent.

**Trace: internal/server/config/doc_engine_config.go** — `internal/server/config/doc_engine_config.go:53-58`

Configured es.hosts and credentials → NewEngine → TLS transport with verification disabled → index/query requests and Basic credentials sent to impersonated endpoint. This source segment establishes the internal/server/config/doc_engine_config.go transition.

```go
// ElasticsearchConfig Elasticsearch configuration
type ElasticsearchConfig struct {
	Hosts    string `mapstructure:"hosts"`
	Username string `mapstructure:"username"`
	Password string `mapstructure:"password"`
}
```

**Broken control: internal/engine/elasticsearch/client.go** — `internal/engine/elasticsearch/client.go:43-58`

Certificate chain and hostname verification are disabled in the shared ES transport, with no verification/CA field in ElasticsearchConfig.

```go
func NewEngine(ctx context.Context, esConfig config.ElasticsearchConfig) (*Engine, error) {
	// Create ES client
	client, err := elasticsearch.NewClient(elasticsearch.Config{
		Addresses: []string{esConfig.Hosts},
		Username:  esConfig.Username,
		Password:  esConfig.Password,
		Transport: &http.Transport{
			MaxIdleConns:          1000,
			MaxIdleConnsPerHost:   300,
			MaxConnsPerHost:       500,
			IdleConnTimeout:       60 * time.Second,
			ResponseHeaderTimeout: 30 * time.Second,
			TLSClientConfig:       &tls.Config{InsecureSkipVerify: true},
			ForceAttemptHTTP2:     true,
		},
	})
```

Counterevidence and remaining uncertainty:
- This does not create remote access without network interception. No traffic was intercepted and default HTTP is a separate transport-security limitation.

Limitations:
- No application/exploit execution or actual image verification.

#### Dataflow

Configured es.hosts and credentials → NewEngine → TLS transport with verification disabled → index/query requests and Basic credentials sent to impersonated endpoint.

**Broken control: internal/engine/elasticsearch/client.go** — `internal/engine/elasticsearch/client.go:43-58`

Certificate chain and hostname verification are disabled in the shared ES transport, with no verification/CA field in ElasticsearchConfig.

```go
func NewEngine(ctx context.Context, esConfig config.ElasticsearchConfig) (*Engine, error) {
	// Create ES client
	client, err := elasticsearch.NewClient(elasticsearch.Config{
		Addresses: []string{esConfig.Hosts},
		Username:  esConfig.Username,
		Password:  esConfig.Password,
		Transport: &http.Transport{
			MaxIdleConns:          1000,
			MaxIdleConnsPerHost:   300,
			MaxConnsPerHost:       500,
			IdleConnTimeout:       60 * time.Second,
			ResponseHeaderTimeout: 30 * time.Second,
			TLSClientConfig:       &tls.Config{InsecureSkipVerify: true},
			ForceAttemptHTTP2:     true,
		},
	})
```

#### Reachability

On-path or DNS/routing attacker against the Elasticsearch connection; HTTPS must be selected. Default lab connection is plain HTTP inside private network.

Existing controls:
- This does not create remote access without network interception. No traffic was intercepted and default HTTP is a separate transport-security limitation.

Limitations:
- Conditional deployment prerequisites remain explicit.

#### Severity

**Medium** — High confidentiality/authority impact is conditional on the stated configuration, existing credential or network position. On-path or DNS/routing attacker against the Elasticsearch connection; HTTPS must be selected. Default lab connection is plain HTTP inside private network.

Actual deployment restrictions can reduce reachability; additional confirmed exposure or runtime mitigation would change the rating.

#### Remediation

Enable certificate validation by default; support trusted CA configuration and hostname verification. Use a verified mTLS tunnel/sidecar plus network isolation until client support is corrected.

Tests:
- Untrusted CA, expired and wrong-host certificates must fail; approved CA and hostname must succeed. Verify no hidden client uses insecure fallback.

## Structural Hardening

The scan also produced derived, unsealed design guidance based on the complete finding collection. These proposals describe options and tradeoffs; they do not indicate that any finding has been remediated.

[Open the structural hardening portfolio](hardening/hardening.md)

## Reviewed Surfaces

| Surface | Risk Area | Outcome | Notes |
| --- | --- | --- | --- |
| Public share beta tokens gain the owner's MCP retrieval scope | Authorization scope escalation | Reported | Source validated; web/src/components/embed-dialog/use-show-embed-dialog.ts:44, web/src/components/embed-dialog/index.tsx:184, internal/service/api_token.go:96, internal/handler/auth.go:138, internal/router/router.go:219, internal/handler/mcp_server.go:99, internal/handler/mcp_server.go:67, internal/handler/mcp_retrieval.go:62. Normal resource permission checks execute, but against the owner. Ordinary protected routes do not accept beta tokens. No exploit executed. |
| API and beta keys survive account deactivation | Account deactivation bypass | Reported | Source validated; internal/admin/service.go:456, internal/dao/api_token.go:48, internal/service/user.go:776, internal/service/stub.go:74, internal/handler/auth.go:172, internal/handler/common.go:79. New password login checks IsActive and existing session tokens are invalidated. This is not an arbitrary cross-tenant bypass. OSS tenant resolver does not add an active-user check. |
| Disabling password login does not block password authentication | Authentication policy enforcement bypass | Reported | Source validated; internal/server/config/api_server_config.go:95, internal/service/system.go:43, internal/router/router.go:167, internal/handler/user.go:236, internal/service/user.go:308. The setting defaults false. Password verification and disabled-user rejection still work; externally enforced gateway restrictions can mitigate reachability. |
| Administrative password reset leaves existing sessions valid | Insufficient session invalidation | Reported | Source validated; internal/admin/service.go:397, internal/service/user.go:515, internal/service/user.go:680, internal/common/token.go:34. Self-service password updates rotate AccessToken; session signatures and 24-hour expiration still work. API key lifecycle is a separate policy. |
| API and Admin listeners ignore configured bind hosts | Unintended network exposure | Reported | Source validated; internal/server/config/api_server_config.go:71, internal/server/config/admin_config.go:38, internal/server/api/server.go:376, internal/server/admin/server.go:85, internal/server/admin/server.go:109. Local lab publishes only 127.0.0.1:18080 and no raw 9380/9381 ports. Listener exposure does not itself bypass application authentication. |
| Elasticsearch HTTPS client skips certificate verification | Improper certificate validation | Reported | Source validated; internal/server/config/doc_engine_config.go:53, internal/engine/elasticsearch/client.go:43. This does not create remote access without network interception. No traffic was intercepted and default HTTP is a separate transport-security limitation. |
| MinIO HTTPS defaults to disabled certificate verification | Unsafe TLS verification default | Reported | Source validated; docker/service_conf.yaml.template:45, internal/server/config/storage_engine_config.go:77, internal/server/config/storage_engine_config.go:116, internal/storage/minio.go:57. Explicit minio.verify:true enables verification and mitigates this issue. Default secure:false does not perform TLS at all. |
| Shared URL fetching and ALLOW_ANY_HOST | SSRF | No issue found | Inspected guards validate schemes/addresses, pin DNS and constrain redirects; ALLOW_ANY_HOST intentionally broadens private access. Local LLM drivers use scheme-only transport, so no universal SSRF guarantee. internal/common/allow_private_host.go:28-65; internal/utility/ssrf.go:31-80; internal/entity/models/lmstudio.go:35-42. |
| OSS SSO, operation audit and roles | Edition-dependent controls | Not applicable | OAuth and audit implementations are !ee no-ops, not bypassed implementations. Community ownership/membership remains. internal/common/stub.go:36-60; internal/server/config/stub.go:90-113; internal/permission/stub.go:27-38. |
| Local and external code execution providers | Execution isolation | Needs follow-up | Local explicitly executes with host-process privileges, operator-selected behavior; no default RCE claim. External Manager/Runner implementation absent; privileged+Docker socket in docker/docker-compose-base.yml:228-257 requires separate dedicated execution host and deployed-image verification. |
| Committed RSA password transport key and session cryptography | Cryptography and secrets | No issue found | RSA key is shared password payload obfuscation, not HMAC signing secret; HTTPS required. Current session HMAC-SHA256 has 86400-second expiry and DB token check. internal/common/password.go:172-240; internal/common/token.go:34-99; internal/server/variable.go:91-106. |
| Unregistered password-change helper | Authentication reachability | Rejected | Conditional old-password validation in UserService.ChangePassword is not reached by registered OSS routes. Active PATCH users/me verifies old password. internal/router/router.go:241-255; internal/service/user.go:651-689,721-744. |
| Unauthenticated admin service reports | Management-plane integrity and limits | Needs follow-up | /api/v1/admin/reports accepts monitoring heartbeats without auth; spoofing and unbounded names warrant isolation/auth/limits. No SSRF/RCE proved: service control methods unimplemented. internal/admin/router.go:39-52; internal/admin/state.go:39-102. |

## Open Questions And Follow Up

- Running binary/image equivalence and actual port, proxy, TLS and ACL behavior were not tested.
  - Follow-up prompt: Validate F01–F07 on a disposable staging deployment built from the selected actual image digest; use two synthetic users and datasets.
- External Sandbox Manager/Runner isolation is outside repository source; local provider has no isolation by design.
  - Follow-up prompt: Review actual pinned Manager/Runner images and verify filesystem, network, credentials, CPU/memory/PID and termination boundaries on a dedicated execution host.
- Admin heartbeat endpoint accepts unauthenticated state reports; monitoring spoofing/unbounded state warrants bounded authenticated management traffic.
  - Follow-up prompt: Review internal/admin/router.go:39-52 and internal/admin/state.go:39-102; define trusted service identities and limits for management reports.
- Not an exhaustive 5870-file audit: all outbound drivers, native parsers, browser rendering, connector OAuth and end-to-end source ACL were not proven.
