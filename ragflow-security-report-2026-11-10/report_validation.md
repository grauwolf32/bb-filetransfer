# Проверка артефактов

Основной HTML: `hardening/ragflow-security-report.html`.

- Chromium desktop 1440px: document width 1440, 11 sections, zero missing fragment targets.
- Chromium mobile 390px: document width 390 after fixing long checklist text wrapping.
- JavaScript page errors: none.
- Settings search `NATS`: 2 matching rows; clear search restores table.
- Checklist check/reset: progress changes to 1/24 and resets; browser-local state only.
- Relative artifact links resolve to regular hardening.md and proposals/identity-capabilities.md; no duplicate HTML IDs.
- Print-to-PDF succeeded as disposable QA output; PDF is not a requested deliverable.
- Desktop/mobile first-page screenshots visually inspected.
- Hardening portfolio JSON and seven relative links validated by its author; all seven supplemental files saved.
- Canonical three JSON files and generated threatmodel.md existed before finalization.
- Source working tree remained clean.

Scope limitation: artifact QA is not application runtime verification. No exploit, integration/load tests, image scans, service restarts or deployment changes were performed. Browser initially failed under macOS process sandbox; an approved local headless run completed the checks. No external assets were loaded by the report.
