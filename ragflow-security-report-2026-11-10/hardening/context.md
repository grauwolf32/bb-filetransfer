# Контекст hardening_final

Scan: b25a7472-7c3e-483f-bc74-7eebcb9723ea. Источник: /Users/ruslan/src/ragflow, HEAD 8cab68a9a3b083da95abb2ea0789b0a5623defaf; рабочее дерево чистое, drift: none. Прочитаны незапечатанные scan-manifest.json, findings.json, coverage.json и threatmodel.md; их формирование продолжается. Производный анализ не заменяет канонические результаты.

| Evidence | Название | Прочитанные источники |
|---|---|---|
| e-share | Публичный beta получает область MCP владельца | web/src/components/embed-dialog/index.tsx:184-187; use-show-embed-dialog.ts:44-52; internal/service/api_token.go:96-107; internal/handler/auth.go:138-149; internal/router/router.go:219-222; internal/handler/mcp_server.go:99-106; internal/handler/mcp_retrieval.go:62-80 |
| e-disable | Отключение пользователя сохраняет API/beta | internal/admin/service.go:460-463; internal/service/user.go:776-795; internal/service/stub.go:78-80 |
| e-login | Запрет парольного входа не применяется | internal/server/config/api_server_config.go:95-121; internal/handler/user.go:244; internal/service/user.go:308-341 |
| e-reset | Admin reset сохраняет текущие сессии | internal/admin/service.go:397-429; internal/service/user.go:515-536,687-689; internal/dao/user.go:112-119 |

IDs обозначают наблюдения исходного кода, а не canonical findings. Содержимое привязано к Git revision; seal/hash финального manifest не заявлен. Статический анализ Go OSS: runtime PoC, benchmark и соответствие deployed image исходникам не проверялись.
