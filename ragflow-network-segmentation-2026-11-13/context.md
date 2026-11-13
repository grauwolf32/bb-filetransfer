# Network hardening context — 2026-11-13

Target directory: /Users/ruslan/recent-work/ragflow
Scope: design proposal for the current local lab. No live configuration, network membership, firewall rules or source files modified.
Runtime: RAGFlow Go v1.0.0-rc3, image digest sha256:931307991475344f61c0d2f2af4c10dd5b37a3cdfa5814737688b8bb8f6a7298. Lab README identifies source snapshot 03c1246150febe6b204b3799dffb3afe52103fb8; this is an unversioned source directory, not an independently proven image/source equivalence.
Podman client/server 6.1.4; rootless:true; Netavark 2.1.0 and aardvark-dns 2.1.0; Fedora 44 podman-machine-os.
Current source configuration inventory:
- compose.yaml — SHA256 bc0f88b5b61e987516311ce7ef20c52553d606bb4b55974452add9b3978fafd5
- config/ragflow.conf — SHA256 fe92ae852575203239f16a30bd31e792cc2b906ee00bdff01957f9ee72be00b2
- config/service_conf.yaml.template — SHA256 bbc1681aaa7a9d321d8a09a735368e3b56dc87c20b93f7930ad71d8579f0a22e
- upstream/docker/entrypoint.sh — SHA256 c3f50b90a437f20fa1fec8b44d589de69e52eb0d72172d952ad04050a6b92864
- upstream/docker/kvrocks-entrypoint.sh — SHA256 6920d61f8e1a05d3805866fdc797096a779bffcbce7dd401d6f75140f74f615e
- upstream/internal/service/admin_client.go — SHA256 9bb47c675bdb838e90577523e6f234787251990e3b3c2a593a88600249742b9a
- upstream/internal/server/bootstrap/runtime.go — SHA256 e9dea6da8b3081c7d307b28c78e4a29650a18a9e63b868867f8077d09c2cae8c
Collection digest: 649e6855c8476d89f3ac93021911e6d2d2acec8a5be759b67f9aea6758618af2 (SHA256 over JSON of sorted-key path/digest inventory in source order).
Raw selected runtime evidence is retained in evidence/runtime.json; all listed input files were opened. No .env or password values retained.

Evidence registry:
- NET — Shared backend and separate outbound membership: podman inspect and network inspect confirm all seven services share internal 10.89.0.0/24; only RAGFlow also has outbound 10.89.1.0/24.
- PORTS — Configured client ports and actual connections: service_conf template + ss confirm MySQL3306, ES9200, MinIO9000, Kvrocks6379, NATS4222. ClickHouse9000 is configured; no established socket was captured in this snapshot, which is not proof it is unused. EXPOSE values are not listener or client-port evidence.
- MONOLITH — Entrypoint and live listeners: nginx80, API9380, admin9381, and ingestor share the same container/network namespace. Admin listens wildcard despite config host127.0.0.1. API and ingestor use localhost9381.
- HEARTBEAT — internal/service/admin_client.go:133 sends POST /api/v1/admin/reports; bootstrap/runtime.go:63 onward starts this client for roles. A future role split must preserve or deliberately redesign that path.
- VALIDATED-F01 — Prior runtime validation confirmed beta MCP dataset metadata disclosure at container-loopback API while Nginx rejects /api/v1/mcp. This design does not fix the authorization issue.
- VALIDATED-F02 — Prior runtime validation confirmed unchanged API key downloads original synthetic document after admin deactivation through normal gateway. Network segmentation does not fix credential lifecycle.

Existing completed source scan b25a7472-7c3e-483f-bc74-7eebcb9723ea context loaded read-only. Original scan target revision 8cab68a9a3b083da95abb2ea0789b0a5623defaf differs from lab rc3. Original scan seal hashes were not revalidated for this design; no claim of a new scan or closure is made.

Read-only network namespace inspection found podman1/podman2 in the rootless Netavark namespace. No candidate network or firewall policy was applied, no namespace-aware packet-filter enforcement or new-network isolation was proven, and no forbidden-port probes or performance benchmarks were run. Empty nft/iptables command output is not used as proof of absence of enforcement.

Primary technical references:
- Podman network options: https://docs.podman.io/en/latest/markdown/podman-network-create.1.html
- Rootless network namespace: https://docs.podman.io/en/latest/markdown/podman-unshare.1.html
- nftables address families and hooks: https://netfilter.org/projects/nftables/manpage.html
Current online docs are latest, so use matching installed help and runtime tests before relying on option defaults.
