# Runtime minimization context — 2026-11-13

Authorized target: /Users/ruslan/recent-work/ragflow.
User request: remove unnecessary runtime tools after we found embedded Python in Vim. No request to remove Bash startup or redesign networking in this turn.

Evidence identity: evidence/verification.json SHA256 8545a600891cebf6bb65932050b3ce54f48337530dc6837c8359bcab33017338.
Base image ID 5b38c06c0877c2508e39bda0db015a87f12ee592a712131069adc5500d4078a3, digest sha256:931307991475344f61c0d2f2af4c10dd5b37a3cdfa5814737688b8bb8f6a7298.
Candidate image ID 5525f66d84f07475b4a34631a753641fef1588af64a98e50e55fdf60f976520c, digest sha256:8803ecb0a91edef2a44b731cc7249adcde080a19b9ec60eedf98b700d7026459.
Application binary unchanged: 69a35469bf70ccd2a78733c86c51aba9e8fc510f3e51a367e5bf0a0512f62ece.
Original scan artifacts remain untouched. The source application revision is still the rc3 snapshot declared by lab README (03c1246150febe6b204b3799dffb3afe52103fb8); image/source equivalence was not rebuilt, but the actual existing and new binary hashes were compared.

Input and changed-file hashes:
- compose.yaml — 9612cb9d0e0d0e0e70cdc690830469ebed8f8e90493f1dc83cae9502a371a1ab
- README.md — e283186f461ac3f0002fe10cf9ec73e1811cd8eaa8090aeb856a951875fb0f65
- config/minimal-image/Containerfile — bd1a8937b338a65d56fd519342d848cd4c3b4c5f285e9c4d952843337243a5a4
- config/minimal-image.lock.json — 39fa0dd8311e49cb5f7499ab0dbd4f98232f1da084cbd1500337a5d4d6eae845
- bin/build-minimal-image.sh — eea1ec8ff6f54f3a646904fadd84ab188533926186e468b2048e9a88be8fb4a8
- bin/verify-minimal-runtime.py — ef03c4efacecf6e7da28e4cee86f7b73c1f97962d0755460baec4bf29d2a94bb

Observed package removal: exactly eight installed packages,141→133. apt --simulate checked before build; no blanket autoremove. Only library/runtime files unneeded for current native document workload were targeted. Essential perl-base remains; this is not absence of all interpreters.
Actual isolated stack: separate seven containers/networks/volumes on localhost18081, then fully removed.
Production-like local lab: only ragflow service recreated at localhost18080. Database backup and original compose copied privately under data/backups/runtime-minimal-2026-11-13, SQL dump600; dump not included in this collection.
Both test runs used fresh synthetic users with full-text-only datasets and TXT/DOCX/PDF fixtures, then deleted fixtures/users.
Before/after original counts: {"knowledgebase":"3","document":"1356","user":"2"} / {"knowledgebase":"3","document":"1356","user":"2"}.
No vector embedding inference retested because original local service was offline. Bionic was briefly opened during investigation and closed again; no model-server settings or new software were installed. No claim that package removal prevents RCE, fixes auth findings, or segments networks.
