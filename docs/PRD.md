# CliniClarity: Product Requirements Document (PRD)
This document serves as the foundational strategic guide for CliniClarity, bridging the gap between clinical complexity and patient literacy through managed AI workflows.

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
