# CliniClarity: Strategic Roadmap (Feb 2026 - Summer 2026)

This document outlines the development trajectory for CliniClarity, moving from the current infrastructure prototyping phase to a fully agentic MVP and subsequent V2.0 expansion.

## 📅 Phase I: The "Connected" MVP (February 2026)
**Goal:** Bridge the gap between the current `lambda_function.py` redaction logic and the Bedrock Knowledge Base.
* **Infrastructure (Terraform):**
    * [ ] **Vector Database:** Provision OpenSearch Serverless collection via Terraform (currently missing in `main.tf`).
    * [ ] **Bedrock Knowledge Base:** Define the `aws_bedrockagent_knowledge_base` resource to consume the `/OUTPUT` S3 bucket.
    * [ ] **IAM Roles:** Expand `lambda_execution_role` in `main.tf` to allow `bedrock:StartIngestionJob`.
* **Backend Engineering:**
    * [ ] **Trigger Integration:** Modify `lambda_function.py` to trigger the Bedrock syncing API immediately after the "Sanitized File Saved" step.
    * [ ] **Library Standardization:** Resolve dependency conflict—Code uses `PyMuPDF` (`fitz`), but documentation cites `ReportLab`. Update `Compliance.md` or refactor code to ensure consistency.

## 🧠 Phase II: The Agentic Brain (March 2026)
**Goal:** Implement the "Interactive Research Assistant" (ReAct Loop) defined in the PRD.
* **Agent Development (LangChain):**
    * [ ] **State Management:** Implement `LangGraph` or `LangChain` memory to handle conversational context (required for "Phase II" in PRD).
    * [ ] **Tool Binding:** Build the custom tool definitions for the **Tavily Search API** to allow the agent to query PubMed when internal confidence is low.
    * [ ] **Citation Logic:** Engineer the prompt template to enforce the "Direct Citations" rule, ensuring every output includes a Record Line # or DOI.
* **Frontend (User Interface):**
    * [ ] **Streamlit/React MVP:** Build a lightweight frontend to allow file upload and chat interaction.
    * [ ] **API Gateway:** Expose the Agent as a REST API for the frontend to consume.

## 🛡️ Phase III: Safety, Auditing & Eval (April 2026)
**Goal:** Validate the "Privacy by Design" and "Clinical Safety" claims before final presentation.
* **Red Teaming:**
    * [ ] **Adversarial Testing:** Attempt to bypass the `Comprehend Medical` redaction using edge-case medical documents (handwritten notes, poor OCR).
    * [ ] **Hallucination Metrics:** Run an evaluation set of 50 medical queries to measure the "Grounding Rate" against the 100% target.
* **Compliance Documentation:**
    * [ ] **Audit Logs:** Enable S3 Access Logs and CloudTrail to prove "In-Transit Encryption" and "Siloed Storage" for the final compliance report.

## 🚀 Phase IV: V2.0 Expansion (Summer 2026)
**Goal:** Expand beyond text-based PDFs into multi-modal capabilities and mobile accessibility.
* **Multi-Modal Ingestion:**
    * [ ] **Medical Imaging:** Integrate **Claude 3.5 Sonnet Vision** capabilities to analyze images (X-Rays, Charts) within the PDF reports, not just text.
* **Platform Expansion:**
    * [ ] **Mobile Optimization:** Refactor the frontend for the "Dedicated Caregiver" persona who needs access on mobile devices during doctor visits.
* **Advanced RAG:**
    * [ ] **Hybrid Search:** Implement hybrid search (Keyword + Semantic) in OpenSearch to better catch specific drug names that vector search sometimes misses.

## 📊 Success Milestones
| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| **Infrastructure Complete** | Feb 28, 2026 | End-to-End Pipeline (Upload -> Redact -> Vectorize) working. |
| **Agent Alpha** | Mar 15, 2026 | ReAct Loop functioning with Tavily/PubMed integration. |
| **Code Freeze** | Apr 20, 2026 | Feature complete; focus shifts to testing and documentation. |
| **Final Demo** | May 05, 2026 | Live demo capability for Capstone/Final Defense. |
