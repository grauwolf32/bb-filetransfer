# Implementation Plan: RAGFlow runtime minimization

## Selected Design And Constraints

User requested removal of unnecessary runtime tooling on 2026-11-13, following verification that Vim embeds working Python3.12. We will derive a separate local image from the unchanged pinned v1.0.0-rc3 image, purge only eight source-reviewed packages, squash layers, verify the resulting image and then replace only the RAGFlow service. Preserve all data volumes, databases, network policy, UI port and existing credentials. This is targeted runtime minimization, not a shell-less redesign or remediation of F01/F02.

## Source Revision And Drift Check

Base reference: docker.io/infiniflow/ragflow@sha256:931307991475344f61c0d2f2af4c10dd5b37a3cdfa5814737688b8bb8f6a7298.
Local base image ID observed: 5b38c06c0877c2508e39bda0db015a87f12ee592a712131069adc5500d4078a3.
Lab README source snapshot: 03c1246150febe6b204b3799dffb3afe52103fb8. Dockerfile/entrypoint/config reopened before implementation. Current actual packages and apt simulated purge checked; no Python shared library dependency in backend ldd. No compiler/rebuild of application code and no release upgrade.

## Affected Components

New lab-owned minimal-image Containerfile and build helper; RAGFlow image reference in compose.yaml; README operation/rollback notes. Do not edit the upstream source snapshot. Purge vim, vim-common, vim-runtime, unzip, iproute2, libpython3.12-minimal, libpython3.12-stdlib, libpython3.12t64. Keep bash/dash, curl/CA certificates, nginx, native parser libraries, fonts and application resources. Avoid blanket autoremove because native dependencies outside Debian metadata may exist.

## Ordered Work Packages

- Capture non-secret image/package baseline and configuration backup.
- Build a squashed image offline from the existing pinned base; verify Python/Vim/Node absence, required commands and direct backend/native startup.
- Record image identity and permitted removed package set; save a database backup privately before service replacement.
- Replace only the RAGFlow service image, preserve original image and rollback configuration.
- Run lab health/login/registration/MCP controls and synthetic document workflow; remove fixtures.
- Record actual results and operational limitations, document rebuild/rollback.

## Compatibility And Migration

The Go binary, nginx configuration, shell entrypoint, model files and data-volume format stay unchanged. Removing iproute2 removes in-container ip/ss diagnostics; host Podman inspection remains available. Removing unzip may affect operator-only commands but no direct production parser subprocess dependency was found. No package installation or application migrations beyond the unchanged entrypoint's normal startup behavior are introduced.

## Tactical Protections During Migration

Retain loopback publication, no-new-privileges, registration disabled and MCP gateway block. Never print .env, Authorization or DB dump contents. Local image rebuild must not send lab credentials or the lab directory as build context. The build context includes only the Containerfile. Preserve upstream base for rollback.

## Tests And Security Validation

Positive checks: required shell/curl/nginx/backend present; backend help starts for supported modes; nginx config validates; post-switch health and ordinary/admin login; upload/parse/download/delete synthetic text and retrieval where real embedding service is available.
Negative checks: removed installed packages, Vim/Python runtime executables/shared libraries, Node/npm absent; base Go binary hash unchanged; gateway MCP remains404, registration disabled.
If embedding endpoint is offline, state this separately, compare baseline behavior and validate full-text ingestion rather than fabricating embedding success.

## Performance And Resource Benchmarks

Measure original/new image size, removed installed package footprint and health/startup behavior. No throughput or memory advantage is claimed without measurement. Squash all layers so removed files are absent from exported runtime layers rather than only hidden by whiteouts.

## Rollout And Rollback

Back up compose.yaml and metadata database locally with restrictive permissions. Retain the original image by digest. Recreate only ragflow. On application regression, restore original image reference and recreate ragflow without deleting volumes. Never use down -v or prune original images.

## Acceptance Criteria

Exactly the intended installed package removals; Vim and libpython absent; application binary unchanged; candidate image starts and healthy lab is restored; data preserved; synthetic fixtures cleaned; measured identities/sizes and rollback documented. F01/F02 and same-container shell/credential risks remain separate.

## Open Decisions

Full shell-less runtime and role/network separation require a different deployment change. Keep Debian Essential perl-base and package management metadata in this targeted change; do not claim absence of all interpreters or prevention of arbitrary-code execution.
