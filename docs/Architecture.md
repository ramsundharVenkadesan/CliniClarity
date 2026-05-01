This document provides a deep dive into the system design, data flow, and security posture of CliniClarity.

# 1. System Overview
CliniClarity is architected as a serverless, event-driven system on **Google Cloud Platform (GCP)**. The core logic is encapsulated in a **Python**-based **FastAPI** application deployed to **Cloud Run**, ensuring high availability and automatic scaling based on request demand.

---

# 2. The Agentic State Machine (LangGraph)
The platform utilizes a cyclic reasoning lifecycle rather than a linear pipeline. The state is managed via a `GraphState` dictionary that tracks the document through various stages of processing.
* **Ingestion Node:** Reads the PDF, extracts text, and generates a document hash for caching.
* **Privacy Node (Presidio):** Localized sanitization of PII/PHI identifiers.
* **Vectorization Node:** Upserts anonymized embeddings into **Pinecone Serverless**.
* **Synthesis Node:** A ReAct loop that coordinates with the **Gemini 3 Flash model** and medical search tools.
* **Audit Node:** Final mathematical verification of the summary using **DeepEval**.

---

# 3. Data Infrastructure
* **Vector Database:** Pinecone Serverless manages high-dimensional embeddings (1536 dimensions) for sub-second retrieval.
* **Data Persistence: Google Cloud Storage (GCS)** stores temporary document summaries in a 15-minute encrypted cache.
* **Secrets & Encryption: Cloud KMS** manages the encryption keys for storage buckets, while **Secret Manager** handles all external API credentials.

---

# 4. Security Topology
CliniClarity employs a layered "Defense in Depth" strategy:
* **Ingress Security: ProtectAI** scans every incoming document and query for prompt injection attacks.
* **Identity: Firebase Authentication** and **JWT** validation ensure only authorized users can access the processing pipeline.
* **Network Isolation:** The application utilizes **Identity-Aware Proxy** logic and strict **IAM** role-based access control.
