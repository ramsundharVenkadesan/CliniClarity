# CliniClarity: Product Requirements Document (PRD)
This document serves as the architectural blueprint for CliniClarity, an agentic AI system designed to bridge the gap between clinical complexity and patient literacy. Unlike traditional RAG applications, CliniClarity is engineered with a Security-First mindset, ensuring that medical document simplification never compromises data sovereignty or clinical integrity.

---

## Executive Summary
CliniClarity transforms dense, jargon-heavy medical reports into empathetic, evidence-based summaries. By utilizing a stateful LangGraph orchestration, the system manages a multi-stage lifecycle that includes deterministic PII redaction, adversarial prompt defense, and real-time medical research via the Model Context Protocol (MCP).

---

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

---

## Technical Stack & Architecture
####Frameworks & Logic
* **Orchestration:** LangGraph (Transitioned from basic LangChain ReAct to stateful tool-calling).
* **API Layer:** FastAPI with asynchronous streaming for real-time user feedback.
* **Research Protocol:** FastMCP connecting to PubMed for peer-reviewed validation.
* **Vector Database:** Pinecone for localized patient context storage.

####Security & Evaluation Layer
* **PII Redaction:** Microsoft Presidio (Analyzer/Anonymizer) running locally to mask PHI before model ingestion.
* **Adversarial Defense:** ProtectAI DeBERTa-v3 and Meta Prompt-Guard-86M for inference-time injection detection.
* **Automated Auditing:** DeepEval for monitoring faithfulness and hallucination rates.

---

## Autonomous Agent Lifecycle 
This section details the two-phase logic that manages the transition from static summary to interactive research.
* **Phase I: Automated Insight Generation (RAG)** 
  * **Trigger:** Successful ingestion and sanitization of the medical PDF.
  * **Process:** PDF data is chunked and stored as vectors in OpenSearch Serverless.
  * **Output:** The LLM uses the vector store to ground a high-level "Highlights Summary" to provide immediate clarity.
* **Phase II: Interactive Research Assistant (ReAct)**
  * **Trigger:** User submits a follow-up query.
  * **Process (ReAct Loop):** 
    * **Thinking:** The agent analyzes the user's intent.
    * **Action:** The agent first queries the internal Vector Store for context.
    * **Augmentation:** If internal data is insufficient, it invokes the Tavily Search API to query PubMed or PMC.
    * **Observation:** Clinical data from external sources is passed back to the LLM.
  * **Output:** A response cited by specific record lines or a medical DOI
## System Architecture: The Data Pipeline
The lifecycle begins with a "Privacy by Design" ingestion process to ensure HIPAA-grade data handling.
* **S3 Ingestion & Trigger:** Medical documents are uploaded to an /INPUT S3 bucket, which immediately triggers a Lambda Function.
* **Automated Redaction (Security):**
    * The Lambda calls AWS Textract to create bounding boxes with exact coordinates for every word.
    * Text is sent to Comprehend Medical (DetectPHI) to identify sensitive entities (MRNs, names, etc.).
    * A final Lambda function matches the PHI to the coordinates and uses the ReportLab library to draw solid black boxes over the text metadata.
* **Vectorization & Bedrock:** Sanitized PDFs are saved to an `/OUTPUT` S3 bucket, triggering the Bedrock Knowledge Bases ingestion job to chunk and store data in OpenSearch.
## Sucess Metrics (KPIs)
| Metric Category | Key Performance Indicator (KPI) | Goal |
|-----------------|----------------------------------|------|
| Accuracy | Grounding Rate | 100% of responses must be traceable to a record line or DOI |
| Trust | Hallucination Rate | <1% occurrence of "General Medical Advice" outside of vetted journals |
| Performance | Inference Latency | Phase I Summary delivered in <10s; Phase II ReAct loop in <15s |
| Security | PHI Redaction Success | Zero sensitive metadata found in the OpenSearch vector store |
| User Value | Query-to-Consultation Ratio | Number of evidence-based questions generated per report uploaded |


