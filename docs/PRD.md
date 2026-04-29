# CliniClarity: Product Requirements Document (PRD)
This document serves as the architectural blueprint for CliniClarity, an agentic AI system designed to bridge the gap between clinical complexity and patient literacy. Unlike traditional RAG applications, CliniClarity is engineered with a Security-First mindset, ensuring that medical document simplification never compromises data sovereignty or clinical integrity.

## Executive Summary
CliniClarity transforms dense, jargon-heavy medical reports into empathetic, evidence-based summaries. By utilizing a stateful LangGraph orchestration on Google Cloud Platform (GCP), the system manages a multi-stage lifecycle that includes deterministic PII redaction, adversarial prompt defense, and real-time medical research via the Model Context Protocol (MCP).

## User Personas (Discovery Phase)
To ensure the product lifecycle is grounded in real-world needs, the following personas represent our primary target audience:
* **The Proactive Patient**
   * **Background:** Recently diagnosed with a complex condition (Ex: chronic illness or post-surgery)
   * **Pain Point:** Receives 20+ page reports filled with administrative data and clinical jargon that feels inaccessible
   * **Goal:** To arrive at their next doctor's consultation with evidence-based questions rather than general anxiety
* **Dedicated Caregiver**
   * **Background:** Managing the health journey of a family member or dependent
   * **Pain Point:** Struggles to provide continuity across different specialists and fragmented medical reports
   * **Goal:** To translate complex lab values into high-level highlights to better manage care plans.

## Technical Stack & Architecture
#### Frameworks & Cloud Infrastructure
* **Cloud Provider:** Google Cloud Platform (Cloud Run, Cloud Storage, Secret Manager, Cloud KMS).
* **Identity & Access:** Firebase Identity Platform.
* **Orchestration:** LangGraph (Stateful RAG Architect) and LangChain (ReAct Medical Assistant).
* **API Layer:** FastAPI with asynchronous Server-Sent Events (SSE) for real-time streaming.
* **Research Protocol:** FastMCP connecting locally to PubMed for peer-reviewed validation.
* **Vector Database:** Pinecone (Serverless 1536-dimensional index) for tenant-isolated context storage.

#### Security & Evaluation Layer
* **PII Redaction:** Microsoft Presidio (Analyzer/Anonymizer) running locally within the container to irreversibly mask PHI before embedding.
* **Adversarial Defense:** ProtectAI DeBERTa-v3 (Hugging Face) acting as an inference-time firewall to block prompt injections.
* **Automated Auditing:** DeepEval for deterministic scoring of faithfulness and hallucination rates.

## Autonomous Agent Lifecycle 
This section details the two-phase logic that manages the transition from static summary to interactive research.

* **Phase I: Automated Insight Generation (RAG Architect)** * **Trigger:** Successful ingestion and sanitization of the medical PDF via the `/summary` endpoint.
  * **Process:** Data is scrubbed by Presidio, chunked, and upserted into Pinecone. LangGraph orchestrates the reasoning loop, drafting a summary and passing it through a DeepEval hallucination check. A Reflection node audits the tone and jargon.
  * **Output:** A cached, clinical-grade "Highlights Summary" streamed back to the UI.

* **Phase II: Interactive Research Assistant (ReAct)**
  * **Trigger:** User submits a follow-up query via the `/question` endpoint.
  * **Process (ReAct Loop):** * **Security Gate:** Query is scanned for adversarial payloads.
    * **Thinking:** The agent analyzes the user's intent.
    * **Action:** The agent queries the Pinecone Vector Store for specific patient context.
    * **Augmentation:** If internal data is insufficient or requires verification, the agent invokes the FastMCP PubMed server.
    * **Observation:** Clinical data from external, peer-reviewed sources is passed back to the Gemini LLM.
  * **Output:** A 6th-grade reading level response cited by specific record lines or a medical DOI.

## System Architecture: The Data Pipeline
The lifecycle begins with a "Privacy by Design" ingestion process to ensure HIPAA-aligned data handling and strict tenant isolation.
* **Ingress & Authentication:** The user authenticates via Firebase. The JWT is validated by FastAPI before any processing begins.
* **Automated Redaction (Security):**
    * The PDF is loaded into memory, and the text is extracted.
    * Microsoft Presidio identifies and replaces sensitive entities (MRNs, names, locations) with irreversible placeholders.
* **Vectorization & Storage:** Sanitized chunks are embedded using Gemini and stored in Pinecone, rigidly bound to the authenticated `user_id` via metadata filtering to prevent cross-contamination.
* **Semantic Caching:** Finalized summaries are hashed and stored in Google Cloud Storage. This bucket is strictly governed by a 1-day TTL lifecycle and encrypted at rest via Customer-Managed Encryption Keys (CMEK) managed by Cloud KMS.

## Success Metrics (KPIs)
| Metric Category | Key Performance Indicator (KPI) | Goal |
|-----------------|----------------------------------|------|
| Accuracy | Grounding Rate | 100% of responses must be traceable to a patient record line or PubMed DOI. |
| Trust | Hallucination Rate | <1% occurrence of "General Medical Advice" failing the DeepEval threshold. |
| Performance | Inference Latency | Phase I Summary delivered in <40s; Phase II ReAct loop in <20s. |
| Security | PHI Redaction Success | Zero sensitive metadata found in the Pinecone vector store or Cloud Logging. |
| User Value | Query-to-Consultation Ratio | Number of evidence-based questions generated per report uploaded. |


