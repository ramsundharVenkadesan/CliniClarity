# CliniClarity: V1.0 Execution Roadmap (Spring 2026)

This document outlines the critical path to delivering the CliniClarity MVP by the end of the Spring 2026 semester. The focus is on a high-integrity, HIPAA-compliant AWS architecture using the Model Context Protocol (MCP) for agent standardization.

## 📅 Phase I: The "Connected" MVP (February 2026)
**Goal:** Bridge the gap between the current `lambda_function.py` redaction logic and the Bedrock Knowledge Base.
* **Infrastructure (Terraform):**
    * [ ] **Vector Database:** Provision OpenSearch Serverless collection via Terraform (currently missing in `main.tf`).
    * [ ] **Bedrock Knowledge Base:** Define the `aws_bedrockagent_knowledge_base` resource to consume the `/OUTPUT` S3 bucket.
    * [ ] **IAM Roles:** Expand `lambda_execution_role` in `main.tf` to allow `bedrock:StartIngestionJob`.
* **Backend Engineering:**
    * [ ] **Trigger Integration:** Modify `lambda_function.py` to trigger the Bedrock syncing API immediately after the "Sanitized File Saved" step.
    * [ ] **Library Standardization:** Resolve dependency conflict—Code uses `PyMuPDF` (`fitz`), but documentation cites `ReportLab`. Update `Compliance.md` or refactor code to ensure consistency.

## 🧠 Phase II: The Agentic Brain & MCP (March 2026)
**Goal:** Implement the "Interactive Research Assistant" (ReAct Loop) using MCP for standardized tool access.
* **MCP Server Implementation (The Connector):**
    * [ ] **PubMed Tooling:** specific Develop a lightweight Python MCP Server (`cliniclarity-mcp`) to expose the Tavily/PubMed search as a standardized **MCP Tool**.
    * [ ] **Patient Context:** Expose the OpenSearch Vector Store retrieval as an **MCP Resource**, allowing the agent to "read" patient data via a standard URI scheme (e.g., `patient://record/{id}`).
* **Agent Development (LangChain on AWS):**
    * [ ] **MCP Client:** Configure the LangChain/Bedrock agent to connect to your local or hosted MCP server to discover tools dynamically.
    * [ ] **State Management:** Implement `LangGraph` memory to maintain conversational context during the ReAct loop.
    * [ ] **Citation Logic:** Engineer the prompt template to enforce the "Direct Citations" rule, ensuring every output includes a Record Line # or DOI.
* **Frontend (User Interface):**
    * [ ] **Streamlit/React MVP:** Build a lightweight frontend to allow file upload and chat interaction.

## 🛡️ Phase III: Optimization, Safety & Final Defense (April - May 2026)
**Goal:** Validate the "Privacy by Design" and "Clinical Safety" claims for final presentation.
* **Performance Optimization:**
    * [ ] **Latency Tuning:** Ensure "Phase I Summary" is delivered in <10s and "Phase II ReAct loop" in <15s by optimizing the MCP server response times.
    * [ ] **Cold Start Mitigation:** Implement Provisioned Concurrency for the Lambda functions if latency targets are missed.
* **Red Teaming & Validation:**
    * [ ] **Adversarial Testing:** Attempt to bypass the `Comprehend Medical` redaction using edge-case medical documents (handwritten notes, poor OCR).
    * [ ] **Hallucination Metrics:** Run an evaluation set of 50 medical queries to measure the "Grounding Rate" against the 100% target.
* **Final Deliverables:**
    * [ ] **Audit Logs:** Enable S3 Access Logs and CloudTrail to prove "In-Transit Encryption" and "Siloed Storage" for the final compliance report.
    * [ ] **Demo Recording:** Record a live, end-to-end demo (Upload -> Redact -> MCP Agent Chat) for the final defense/presentation.

## 📊 Success Milestones
| Milestone | Target Date | Deliverable |
| :--- | :--- | :--- |
| **Infrastructure Complete** | Feb 28, 2026 | End-to-End Pipeline (Upload -> Redact -> Vectorize) working. |
| **MCP Agent Alpha** | Mar 15, 2026 | ReAct Loop functioning via MCP Server with Tavily/PubMed. |
| **Code Freeze** | Apr 15, 2026 | Feature complete; focus shifts to testing and bug fixes. |
| **Final Release (V1.0)** | May 05, 2026 | Production-ready MVP with full documentation and audit logs. |
