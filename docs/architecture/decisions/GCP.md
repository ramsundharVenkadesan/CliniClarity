# Architecture Decision Record: Standardizing on Google Cloud Platform (GCP) for Core Infrastructure

* **Status:** Accepted
* **Date:** 2026-03-28

## Context
CliniClarity requires a cloud-native hosting environment capable of executing a complex, long-running agentic reasoning loop (LangGraph) via a FastAPI backend. The infrastructure must handle high-dimensional vector operations, stream Server-Sent Events (SSE) reliably, and enforce strict, HIPAA-aligned data lifecycle and encryption standards without incurring massive administrative overhead.

## Decision: Implement GCP for Compute, Storage, and Identity
We have chosen Google Cloud Platform (GCP) as the primary cloud provider, utilizing Cloud Run, Cloud Storage, Secret Manager, Cloud KMS, and Firebase Identity Platform, fully orchestrated via Terraform.

## Decision Rationale
* **Serverless Container Orchestration:** Cloud Run v2 allows us to deploy our Python-based LangGraph containers with scale-to-zero capabilities. This handles the heavy memory requirements (4Gi) of our local HuggingFace prompt-injection scanner and LangChain dependencies without the operational burden of managing Kubernetes nodes.
* **Security & Key Management (HIPAA Alignment):** GCP natively supports Customer-Managed Encryption Keys (CMEK) via Cloud KMS. By binding these keys directly to our Cloud Storage cache buckets and enforcing 1-day TTL lifecycles natively in Terraform, we mathematically ensure temporary medical data is encrypted at rest and automatically purged.
* **Identity & Credential Hygiene:** GCP allows us to utilize Workload Identity Federation (WIF) and direct IAM Service Account bindings. This completely eliminates the need for static JSON keys, bypassing organizational policy restrictions and dramatically reducing the risk of credential leakage. 
* **Native Authentication Synergy:** Firebase Authentication acts as a seamless, strict ingress gatekeeper. It natively validates Identity Platform JWTs directly in the Cloud Run service, blocking unauthorized domains and API traffic before it ever hits the cognitive pipeline.

## Alternative Considered
* **Amazon Web Services (AWS) via ECS Fargate / Lambda:** AWS is the industry standard, but for this specific architecture, it presented friction. AWS Lambda enforces strict 15-minute timeouts and has notoriously difficult deployment package limits (250MB), which makes deploying heavy AI libraries like `torch`, `deepeval`, and `transformers` incredibly difficult without complex Docker workarounds. Alternatively, AWS ECS Fargate solves the container size issue but requires significantly more boilerplate networking infrastructure (VPCs, Subnets, ALBs, NAT Gateways) compared to the immediate, secure, public-facing ingress provided out-of-the-box by Google Cloud Run.
