# "Tell me about yourself" / Brief intro script

Built from your resume, not invented — every claim below is a line you already have written down. Practice this out loud, don't memorize it word-for-word (it should sound like you talking, not a recital).

## ~75-90 second version (use this as the default)

"I'm a Staff Software Engineer at RapidAI, where for the last few years I've been building the backend and distributed-systems foundations for a mission-critical healthcare AI platform — the kind of system where downtime means hospitals don't get their AI results back.

I own the shared Go platform that over 40 backend services are built on — logging, database access, HTTP, telemetry, object storage — and I designed the pipeline that delivers AI inference results from multi-region cloud down to on-prem hospital PACS systems. I also designed the HA/failover architecture across AWS — ALB, Global Accelerator, EKS, S3 with cross-region replication — that keeps inference running through network and region outages, targeting 99.99% availability across 2,000 hospitals in 6 regions. Beyond the architecture work, I set the data-architecture direction for our high-throughput workloads, evaluating CockroachDB and YugabyteDB against Postgres, and I led the OpenTelemetry rollout across teams that cut incident triage time by about 30 minutes per engineer.

Before RapidAI, I spent five years at ZEDEDA building the cloud control plane for 15,000 to 20,000 edge devices. I led the team that migrated our core microservices off Cassandra onto Postgres for a 3x performance improvement, and built the security layer — HashiCorp Vault, ECDH key exchange, signature verification — protecting edge-to-cloud communication.

[Close — customize per company, don't leave this generic:] That's what's brought me here — I'm looking at [Plenful / Mercor] because ___."

## Notes on delivery

- **The last line is a placeholder on purpose** — fill in a real reason per company before each interview. For Plenful (healthcare automations), your PACS/hospital-delivery and HA work is a near-literal domain match — say that directly rather than something generic like "great culture." For Mercor (security-focused interviewer), lead the close with the Vault/ECDH/signature-verification line instead of burying it in the middle.
- If asked to go deeper ("walk me through that in more detail"), the next layer to add is the Netflix Conductor orchestration work (50+ multi-stage DAG workflows spanning edge and cloud) and the ArgoCD/GitOps CI/CD work (cut release-incidents 80%+, saved ~1hr/release) — don't front-load those, they're the expansion pack if asked.
- Keep it under 90 seconds unprompted. If you're still talking at 2 minutes without being asked to continue, you've lost the interviewer's attention budget for the rest of the conversation.
- This script deliberately leads with *scope and stakes* (mission-critical healthcare, 2,000 hospitals) before *mechanism* (Go libraries, HA architecture) — that ordering is what makes a Staff-level intro land; leading with mechanism first reads as a mid-level intro.
