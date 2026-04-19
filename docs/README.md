# CliniClarity: From Medical Anxiety to Medical Literacy

**A personal health research assistant designed to be a bridge between a clinical visit and a patient's home life.**

## 📋 Product Vision and Strategy 
CliniClarity is not a diagnostic engine; it is a specialized AI Security Architect-led research platform engineered to help patients navigate complex medical journeys with grounded, verifiable intelligence.

### The Problem: Dense Jargon and "Dr.Google
* **Medical Complexity:** Patients receive dense reports where critical insights are buried in peer-to-peer clinical shorthand.
* **The Hallucination Risk:** General LLMs often "guess" or prioritize SEO-optimized blogs over clinical reality.
* **Security Vulnerabilities:** Standard AI wrappers are susceptible to prompt injections and PII leaks, making them unsuitable for healthcare.

### The Solution: Deterministic & Grounded Intelligence
CliniClarity provides an evidence-based pipeline where every response is mathematically and clinically verified.
* **Security-First:** Implements local adversarial defense to block prompt injections before they reach the reasoning engine.
* **Clinically Grounded:** Uses a dedicated FastMCP server to query high-authority databases like PubMed.
* **Verified Output:** Utilizes DeepEval to audit for hallucinations, ensuring the final answer strictly adheres to the provided medical context.

## 🛠️ Agent Architecture

#### Visualizing the Pipeline
```mermaid
    graph TD
    %% Global Styles
    classDef userNode fill:#ffffff,stroke:#000,stroke-width:2px,color:#000,font-weight:bold;
    classDef security fill:#fff1f1,stroke:#e57373,stroke-width:2px,color:#b71c1c;
    classDef core fill:#f0f7ff,stroke:#64b5f6,stroke-width:2px,color:#0d47a1;
    classDef tool fill:#f6fff8,stroke:#81c784,stroke-width:2px,color:#1b5e20;
    classDef final fill:#2e7d32,stroke:#1b5e20,stroke-width:2px,color:#fff,font-weight:bold;
    classDef block fill:#c62828,stroke:#b71c1c,stroke-width:2px,color:#fff;
    classDef ingestion fill:#fff9db,stroke:#f59f00,stroke-width:2px,color:#862e00;

    %% 1. Secure Ingestion Pipeline
    User((User)):::userNode -->|Upload PDF| PDF[PDF Parser/PyMuPDF]:::ingestion
    
    subgraph SI [🔐 SECURE INGESTION LAYER]
        PDF --> Presidio[Microsoft Presidio: Local PII Redaction]:::security
        Presidio -->|Anonymized Text| Embed[Gemini-Embedding-001]:::ingestion
        Embed --> VectorDB[(Pinecone: Anonymized Vector Store)]:::tool
    end

    %% 2. Adversarial Query Defense
    User -->|Question| API[FastAPI Gateway]
    
    subgraph SG [🛡️ ADVERSARIAL DEFENSE LAYER]
        API --> PI[ProtectAI: Injection Scan]:::security
        PI -->|Fail| Block1[❌ BLOCKED]:::block
        PI -->|Pass| MI[Semantic: Intent Route]:::security
        MI -->|Fail| Block2[❌ OFF-TOPIC]:::block
    end

    %% 3. Agentic Reasoning
    subgraph AC [🧠 AGENTIC REASONING]
        MI -->|Pass| Agent[LangGraph Controller]:::core
        Agent <--> LLM[Gemini 3 Flash]:::core
        
        subgraph TL [🛠️ MCP & DATA TOOLS]
            Agent <--> VectorDB
            Agent <--> PubMed[MCP: PubMed Server]:::tool
        end
    end

    %% 4. Quality Assurance
    subgraph VQ [✅ QUALITY ASSURANCE]
        Agent --> Eval[DeepEval: Hallucination Check]:::core
        Eval -->|Pass| Out[Final 6th-Grade Answer]:::final
        Eval -->|Fail| Agent
    end

    %% Apply Container Styles
    style SI fill:none,stroke:#f59f00,stroke-dasharray: 5 5
    style SG fill:none,stroke:#e57373,stroke-dasharray: 5 5
    style AC fill:none,stroke:#64b5f6,stroke-dasharray: 5 5
    style VQ fill:none,stroke:#9575cd,stroke-dasharray: 5 5
```
---

#### 🚀 Key Technological Pillars
Below is the architectural blueprint of CliniClarity, illustrating the flow from secure ingestion to verified synthesis.
1. **The Agentic Core: LangGraph & Native Tool Calling**
   We moved beyond linear chains to a State Machine architecture using LangGraph.
     *  **Deterministic Flow:** Each stage—from ingestion to synthesis—is a verifiable node in the graph.
     *  **Native Tool Calling:** Deprecated legacy ReAct text-parsing in favor of Native JSON Tool Calling, reducing hijacking risks and improving response latency.
2. **Multi-Layered Guardrails (Adversarial Defense)**
   To ensure HIPAA-grade safety, the system implements a "Defense-in-Depth" strategy:
     * **Prompt Injection Defense:** Integrated a local Hugging Face SLM (ProtectAI DeBERTa) to block adversarial attacks before they reach the LLM.
     * **Semantic Routing:** Uses cosine similarity math to ensure the system strictly only processes clinical and biological queries.
3. **FastMCP: Medical Knowledge Integration**
   Utilizing the **Model Context Protocol (MCP)**, CliniClarity securely bridges the gap between patient data and external clinical literature.
     * **PubMed Server:** A standalone MCP server queries the National Library of Medicine directly, providing the agent with peer-reviewed verification of medical terms found in the user's report.
4. **Verification & QA: DeepEval**
   Every response undergoes an automated hallucination check. Using **DeepEval**, the system measures "Faithfulness" by comparing the generated answer against the retrieved document chunks, preventing the model from inventing clinical findings.

---

#### 🛠️ The Tech Stack
1. **Core AI & Orchestration (Agentic RAG)**
   * **Orchestration:** LangGraph (State Machine logic) & LangChain (Tool binding)
   * **Reasoning Engine**: Gemini 3 Flash (Native Tool Calling)
   * **Knowledge Retrieval:** Tiered RAG (Internal Pinecone Vector Store + External PubMed MCP)
   * **Verification:** DeepEval (Deterministic Hallucination & Faithfulness auditing)
2. **Security & Guardrails**
   * **Adversarial Defense:** ProtectAI DeBERTa (Local Prompt Injection detection)
   * **Data Privacy:** **Microsoft Presidio** (Local PII/PHI redaction)
   * **Intent Routing:** Semantic Vector Router (Cosine Similarity topic enforcement)
3. **Data & Infrastructure**
   * **Vector Database:** Pinecone (Serverless)
   * **Infrastructure as Code:** Terraform (AWS VPC & EC2 orchestration)
   * **API Layer:** FastAPI with Asynchronous Server-Sent Events (SSE)

---

#### 🔒 Security & HIPAA-First Data Pipeline
To ensure Protected Health Information (PHI) is never exposed to public models or unauthorized cloud logs, CliniClarity implements a "Local-First" automated redaction pipeline. This architecture satisfies HIPAA "Safe Harbor" standards by de-identifying data before it enters the RAG ecosystem.

* **Deterministic PII/PHI Redaction:** Instead of relying on cloud-based NLP, CliniClarity utilizes a local instance of Microsoft Presidio. This engine performs Named Entity Recognition (NER) to identify 18+ types of identifiers (Names, SSNs, Phone Numbers, Locations) directly within the secure application boundary.

* **Zero-Egress Sanitization:** The redaction process uses the Presidio-Anonymizer to replace sensitive metadata with generic placeholders (e.g., [REDACTED_NAME]) or cryptographic hashes. This ensures that the text remains clinically useful for the LLM while being mathematically stripped of identity.

* **Safe Harbor Compliance:** By scrubbing data locally before it reaches the Gemini Embedding or Pinecone Vector Store, the system ensures that no PII is ever used for model training or stored in a third-party database.

* **Immutable Redaction (PDF):** For document visualization, the system utilizes the ReportLab library to draw physical, non-recoverable black boxes over identified PHI coordinates, ensuring sensitive data cannot be recovered via text highlighting or metadata scraping.

---

#### 🚀 Key Strategic Benefits
| Feature | Traditional LLMs / Search Engines | CliniClarity (Our Product) | PLM Strategic Value |
|--------|------------------------------------|----------------------------|---------------------|
| **Information Source** | Guesses based on patterns or SEO-optimized blogs | Grounded in patient records and peer-reviewed PubMed literature | **Trust:** Reduces medical anxiety by ensuring 100% clinical validity. |
| **Logic & Reasoning** | Single-shot responses prone to hallucinations | Agentic RAG: Multi-turn reasoning with native tool calling | **Accuracy:** Eliminates "guessing" by forcing the model to verify facts against clinical data. |
| **Data Privacy** | Sensitive data may be used to train public models | Local PII/PHI redaction via Microsoft Presidio before cloud egress | **Compliance:** Built with "Privacy by Design" to meet HIPAA Safe Harbor standards. |
| **Adversarial Security** | Vulnerable to prompt injections and jailbreaks | Deterministic Guardrails: Local ProtectAI scan and Semantic Routing | **Safety:** Prevents system hijacking and ensures the agent remains strictly within the medical domain. |
| **Auditability** | Provides general advice without specific source links | Every response is cited with a specific DOI and evaluated via DeepEval | **Reliability:** Empowers patients with verifiable evidence for physician consultations. |
| **Knowledge Retrieval** | Limited to the model's training cutoff date | Real-time Tiered Retrieval: Vector Store (Internal) + FastMCP (External) | **Efficiency:** Prioritizes specific patient context while augmenting with the latest medical research. |

---

## Cloud Architecture
The application is deployed as a fully managed, serverless architecture on Google Cloud Platform (GCP). It utilizes Cloud Run for scalable compute, Firebase for secure identity management, and KMS-encrypted Cloud Storage to safely handle semantic caching.

```mermaid
graph TD
    %% Styling
    classDef gcp fill:#4285F4,stroke:#fff,stroke-width:2px,color:#fff;
    classDef storage fill:#FBBC05,stroke:#fff,stroke-width:2px,color:#000;
    classDef security fill:#8F00FF,stroke:#fff,stroke-width:2px,color:#fff;
    classDef external fill:#34A853,stroke:#fff,stroke-width:2px,color:#fff;
    classDef public fill:#EA4335,stroke:#fff,stroke-width:2px,color:#fff;
    classDef config fill:#607D8B,stroke:#fff,stroke-width:2px,color:#fff;
    classDef apis fill:#A142F4,stroke:#fff,stroke-width:1px,color:#fff;

    %% ===== EXTERNAL ENTITIES =====
    Users("🌍 End Users<br/><br/>Web Browser Access"):::public

    subgraph ThirdParty["🔌 External APIs & Services"]
        direction TB
        Pinecone["<b>Pinecone</b><br/>Vector Database<br/>━━━━━━━━━━<br/>Index: cliniclarity<br/>Dimension: 1536<br/>Type: Serverless"]:::external
        LangChain["<b>LangSmith</b><br/>LLM Observability<br/>━━━━━━━━━━<br/>Endpoint: api.smith.langchain.com<br/>Project: cliniclarity-production"]:::external
        HuggingFace["<b>Hugging Face</b><br/>Model Inference<br/>━━━━━━━━━━<br/>Token Auth Required"]:::external
        GoogleAI["<b>Google AI</b><br/>GenAI & Core APIs<br/>━━━━━━━━━━<br/>API Key Auth"]:::external
    end

    subgraph GCP["<b>Google Cloud Platform</b><br/>Project: cliniclarity | Region: us-central1"]
        direction TB
        
        %% ===== API LAYER =====
        subgraph EnabledAPIs["📋 Enabled Google Cloud APIs"]
            APIList["Compute Engine API<br/>Cloud Storage API<br/>Cloud KMS API<br/>Cloud Run API<br/>Firebase API<br/>Identity Platform API"]:::apis
        end

        %% ===== IDENTITY & AUTH =====
        subgraph Identity["🔐 Identity & Access"]
            direction LR
            ServiceAccount["<b>Application Service Account</b><br/>━━━━━━━━━━━━━━<br/>cliniclarity-app-service<br/>Runtime identity for Cloud Run"]:::security
            StorageSA["<b>Storage Service Agent</b><br/>━━━━━━━━━━━━━━<br/>GCS-managed service account<br/>Handles bucket encryption"]:::security
        end

        subgraph Firebase["🔥 Firebase & Authentication"]
            direction LR
            FirebaseProj["<b>Firebase Project</b><br/>━━━━━━━━━━━━━━<br/>Backend services"]:::security
            WebClient["<b>Web Application</b><br/>━━━━━━━━━━━━━━<br/>CliniClarity Web App<br/>Firebase SDK client"]:::security
            AuthMethods["<b>Authentication Methods</b><br/>━━━━━━━━━━━━━━<br/>✓ Email / Password<br/>✓ Google Sign-In"]:::security
            FirebaseProj --- WebClient
            FirebaseProj --- AuthMethods
        end

        %% ===== COMPUTE =====
        subgraph Compute["⚙️ Compute Layer"]
            CloudRunService["<b>Cloud Run Service</b><br/>━━━━━━━━━━━━━━<br/>Container: cliniclarity-app:latest<br/>Port: 8080<br/>Ingress: All traffic allowed"]:::gcp
            
            subgraph EnvConfig["📦 Container Environment"]
                EnvVars["<b>Runtime Configuration</b><br/>━━━━━━━━━━━━━━<br/>GOOGLE_API_KEY<br/>INDEX_NAME<br/>LANGCHAIN_API_KEY<br/>LANGCHAIN_PROJECT<br/>LANGCHAIN_ENDPOINT<br/>HUGGINGFACE_TOKEN<br/>CACHE_BUCKET_NAME<br/>FIREBASE_API_KEY<br/>FIREBASE_AUTH_DOMAIN"]:::config
            end
            CloudRunService --> EnvConfig
        end

        %% ===== ARTIFACT STORAGE =====
        subgraph Registry["📦 Container Registry"]
            ArtifactRegistry["<b>Artifact Registry</b><br/>━━━━━━━━━━━━━━<br/>Format: Docker<br/>Repository: cliniclarity-app"]:::storage
        end

        %% ===== DATA & SECURITY =====
        subgraph StorageLayer["💾 Storage & Encryption"]
            direction LR
            KMS["<b>Cloud KMS</b><br/>━━━━━━━━━━━━━━<br/>Key Ring: cliniclarity-cache<br/>Key: document-encryption<br/>Rotation: 9 days"]:::security
            CacheBucket["<b>Cloud Storage</b><br/>━━━━━━━━━━━━━━<br/>Bucket: doc-cache<br/>Lifecycle: 1 day retention<br/>CMEK Encryption Enabled"]:::storage
        end
    end

    %% ===== CONNECTIONS & RELATIONSHIPS =====

    %% User Traffic Flow
    Users -->|"HTTPS Request<br/>(Public Access)"| CloudRunService
    
    %% IAM Bindings
    CloudRunService -->|"Runs with Identity"| ServiceAccount
    ServiceAccount -->|"Firebase Admin<br/>(roles/firebaseauth.admin)"| FirebaseProj
    
    %% Storage & Encryption Flow
    CloudRunService -->|"Document Caching<br/>(Read / Write)"| CacheBucket
    CacheBucket -->|"Encrypted At Rest<br/>(CMEK)"| KMS
    StorageSA -->|"Key Access<br/>(cryptoKeyEncrypterDecrypter)"| KMS
    
    %% Container Image Flow
    CloudRunService -->|"Pulls Container Image"| ArtifactRegistry
    
    %% External API Calls (from Container)
    EnvConfig -->|"Vector Operations"| Pinecone
    EnvConfig -->|"Tracing & Monitoring"| LangChain
    EnvConfig -->|"Model Inference"| HuggingFace
    EnvConfig -->|"GenAI APIs"| GoogleAI
    EnvConfig -->|"Auth Config"| WebClient

    %% API Enablement (Logical Dependency)
    GCP -.->|"Services Enabled"| EnabledAPIs

    %% ===== LEGEND =====
    subgraph Legend[" "]
        direction LR
        L1["🔵 GCP Compute"]:::gcp
        L2["🟡 GCP Storage"]:::storage
        L3["🟣 Security / IAM"]:::security
        L4["🟢 External Services"]:::external
        L5["🔴 Public Internet"]:::public
        L6["⚪ Configuration"]:::config
    end
```


## 🔒 Security & HIPAA-First Standards
To ensure Protected Health Information (PHI) is never exposed to public models or unauthorized cloud logs, CliniClarity implements a "Local-First" automated redaction pipeline. This architecture satisfies HIPAA "Safe Harbor" standards by de-identifying data before it enters the RAG ecosystem.

* **Deterministic PII/PHI Redaction:** Instead of relying on cloud-based NLP, CliniClarity utilizes a local instance of Microsoft Presidio. This engine performs Named Entity Recognition (NER) to identify 18+ types of identifiers (Names, SSNs, Phone Numbers, Locations) directly within the secure application boundary.

* **Zero-Egress Sanitization:** The redaction process uses the Presidio-Anonymizer to replace sensitive metadata with generic placeholders (e.g., [REDACTED_NAME]) or cryptographic hashes. This ensures that the text remains clinically useful for the LLM while being mathematically stripped of identity.

* **Safe Harbor Compliance:** By scrubbing data locally before it reaches the Gemini Embedding or Pinecone Vector Store, the system ensures that no PII is ever used for model training or stored in a third-party database.

* **Immutable Redaction (PDF):** For document visualization, the system utilizes the ReportLab library to draw physical, non-recoverable black boxes over identified PHI coordinates, ensuring sensitive data cannot be recovered via text highlighting or metadata scraping.
  
* **Customer-Managed Encryption Keys (CMEK):** All temporary data and semantic caching stored in Google Cloud Storage is encrypted at rest using Google Cloud KMS, with rigorous 9-day key rotation schedules and strict 1-day lifecycle deletion rules.
  
* **Adversarial Defense:** Every user query is scanned by ProtectAI to detect prompt injections, ensuring the agent cannot be manipulated into revealing system prompts or bypassing clinical guardrails.
  
* **Least Privilege Identity:** Cloud Run services execute under a dedicated Google IAM Service Account (cliniclarity-app-service), granting access only to the specific resources and Firebase administration privileges required for runtime operations.
  
## 👥 The Team
This product was developed by a cross-functional team with expertise across the full software lifecycle:
* **Greti:** Compliance Documentation
* **Ramsundhar:** Cloud Architecture and Agentic AI

## Technical Appendix

### Orchestration: LangChain & Agentic Logic
To manage the complex clinical reasoning required for healthcare, CliniClarity utilizes **LangGraph** as its core orchestration framework. This allows the system to move beyond linear chains into a robust, cyclic state machine.
* **State Management:** Every interaction is managed as a discrete state within the graph. This ensures that the context from the initial PDF ingestion remains persistent and immutable throughout the follow-up research phase.
* **Self-Correction Loop:** The graph includes conditional edges that route responses through a DeepEval node. If the "Faithfulness" score falls below a specific threshold, the state is routed back to the reasoning engine for refinement, preventing hallucinations before they reach the UI.
* **Native Tool Calling:** Unlike traditional ReAct loops that parse raw text, we utilize Native JSON Tool Calling. This forces the model to interact with external systems (like PubMed) using strictly typed schemas, significantly reducing the risk of tool-hijacking and parsing errors.

---

### Infrastructure as Code (IaC): Terraform
To ensure the product can be deployed reliably across different environments (Dev, QA, Production), the entire Google Cloud architecture is defined and deployed via **Terraform**.
* **Serverless Compute Provisioning:** Terraform handles the automated deployment of Google Cloud Run v2 services, pointing directly to versioned container images stored in Google Artifact Registry.
* **Integrated Identity & Auth:** Firebase Projects, Web Apps, and Identity Platform configurations (supporting Email/Password and Google Sign-In) are fully automated and bound to the application's environment variables natively within the Terraform state.
* **Secure Storage Infrastructure:** GCS buckets utilized for semantic caching are provisioned with 1-day TTL lifecycle rules and strictly enforced Uniform Bucket-Level Access.
* **Automated Encryption Bindings:** Terraform dynamically provisions Cloud KMS KeyRings and CryptoKeys, automatically attaching the required cryptoKeyEncrypterDecrypter IAM roles to the underlying storage service agents to ensure seamless CMEK encryption without manual intervention.

---
  
## Core System Components
* **Gemini 3 Flash:** Serves as the high-speed reasoning engine, selected for its massive context window and native support for asynchronous tool calling.

* **FastMCP (Model Context Protocol):** Orchestrates the connection between the LLM and the National Library of Medicine. By running PubMed as a standalone MCP server, we decouple the knowledge retrieval logic from the core application.

* **Microsoft Presidio:** A localized PII/PHI redaction engine that identifies and scrubs 18+ types of sensitive identifiers at the point of ingestion, ensuring HIPAA "Safe Harbor" compliance without sending raw data to the cloud.

* **Pinecone:** A high-performance vector database that stores the anonymized embeddings of clinical reports, enabling sub-second Retrieval-Augmented Generation (RAG).

* **DeepEval:** A specialized testing framework used to objectively audit the agent's output. It acts as the final "clinical auditor," measuring the factual alignment between the generated summary and the source medical records.

* **Google Cloud Run:** A fully managed serverless compute platform that auto-scales the containerized LangGraph application natively, abstracting away server administration while ensuring rapid scale-up for concurrent users.
  
* **Firebase Identity Platform:** Secures user access with enterprise-grade authentication via Google Sign-In and standard credentials, deeply integrated with the application's service accounts.

