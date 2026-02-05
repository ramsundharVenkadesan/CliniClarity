# CliniClarity: From Medical Anxiety to Medical Literacy

**"A personal health research assistant designed to be a bridge between a clinical visit and a patient's home life."**

## 📋 Product Vision and Strategy 
CliniClarity is not a diagnostic engine; it is a specialized research librarian engineered to help patients navigate complex medical journey

### The Problem: Dense Jargon and "Dr.Google
* **Medical Complexity:** Patients often receive 20+ page medical or imaging reports where critical insights are buried. 
* **Information Gap:** Reports are written for billing and peer-to-peer clinical communication, not for patient comprehension
* **Unverified Sources:** When turning to search engines, patients encounted a mix of "Dr.Google" anecdotes, unverified blogs, and marketing that lacks clinical validity

### The Solution: Grounded Intelligence
Unlike general LLMs that may hallucinate or prioritize SEO content, CliniClarity provides grounded, evidence-based information.
* **Context Aware:** The assistant understands the specific context of the user's health report before searching for answers
* **Authority-First:** Prioritizes peer-reviewed status and impact factor by querying high-authority databases like PubMed or PMC

## 🛠️ Product Architecture
The product lifecycle is built on a "Privacy by Design" framework, ensuring healthcare-grade security and technical transparency
#### The Agent Lifecycle
1. **Automated Insight Generation (RAG):** Upon document upload, the system intiates a Retrieval-Augmented Generation (RAG) pipline to synthesize the report
     *  The PDF data is chunked and converted into vectors (embeddings) stored within OpenSearch Serveless
     *  The LLM uses the vector store to ground results, automatically extracting key bio-markers and translating complex lab values into a high-level summary for the user
     * This phase ensures the patient receives instant clarity on their medical reports
2. **Interactive Research Assistant (ReAct):** Once the summary is provided, the system transitions into an autonomous agent to handle follow-up questions (Ex: _"What does this specific white blood cell count mean for my diagnosis?"_)
     * The agent first queries the OpenSearch vector store to retrieve specific context from the user's uploaded medical report
     * The LLM follows a Thinking -> Action -> Observation loop to determine if the internal record provides enough information or if external validation is required
     * If the internal report lacks necessary clinical background, the agent executes a search tool to query high-authority databases like PubMed
     * The result from PubMed is passed back to LLM as part of the observation, ensuring the final answer is a synthesis fo patient's data and peer-reviewed literature
     * Every response is cited with a specific DOI from the medical journal to ensure 100% auditability.
* **Tech Stack**: Built using AWS Bedrock, OpenSearch Serverless, and Claude Sonnet/Nova Pro
#### Security & HIPAA-First Data Pipeline
To ensure sensitive data is never used to train public models, CliniClarity implements an automated redaction pipeline.
* **PII/PHI Redaction:** A dedicated Lambda function matches PHI found by AWS Comprehend Medical to coordinates provided by AWS Textract
* **Sanitization:** Uses the ReportLab library to draw solid black boxes over sensitive metadata, ensuring it cannot be searched or highlighted.

## 🚀 Key Benefits
| Feature | Traditional LLMs / Search Engines | CliniClarity (Our Product) | PLM Strategic Value |
|--------|----------------------------------|---------------------------|---------------------|
| **Information Source** | Guesses based on patterns or SEO-optimized blogs | Grounded in patient records and vetted medical journals | **Trust:** Reduces medical anxiety by ensuring 100% clinical validity |
| **Logic & Reasoning** | Single-shot responses often prone to hallucinations | ReAct Loop: Thinking → Action → Observation before answering | **Accuracy:** Forces the model to reason through clinical steps before delivery |
| **Data Privacy** | Sensitive data may be used to train public models | Healthcare-grade security with automated PII/PHI redaction | **Compliance:** Built with Privacy by Design to meet HIPAA-grade standards |
| **Traceability** | Provides general advice without specific source links | Every statement is directly linked to a record line or a DOI | **Auditability:** Empowers patients with exact evidence for doctor consultations |
| **Knowledge Retrieval** | Limited to the model's training cutoff date | Tiered Retrieval: Vector Store (Internal) + PubMed (External) | **Efficiency:** Prioritizes user context first, augmenting with external data only when needed |

## 👥 The Team
This product was developed by a cross-functional team with expertise across the full software lifecycle:
* **Bruno:** Containerization and Infrastructure
* **Niall:** User research and HIPAA Compliance
* **Greti:** Machine Learning, Testing and QA
* **Ramsundhar:** Cloud Architecture and Agentic AI

## Technical Appendix
#### Orchestration: LangChain & Agentic Logic
To manage the complex ReAct (Reasoning and Acting) loop, we utilize LangChain as the core orchestration framework. This allows us to move beyond simple chat interfaces into autonomous problem-solving.
* **State Management:** LangChain manages the conversational memory and the "state" of the research assistant, ensuring that follow-up questions maintain the context of the initial medical report.
* **Tool Binding:** We use LangChain to bind the Tavily Search API and PubMed as executable tools that the LLM can "decide" to call when internal context from the vector store is insufficient.
* **Prompt Engineering:** LangChain templates are used to enforce the Thinking -> Action -> Observation cycle, preventing the model from providing unverified medical advice by strictly defining its persona as a "Research Librarian".
#### Infrastructure as Code (IaC): Terraform
To ensure the product can be deployed reliably across different environments (Dev, QA, Production), the entire AWS architecture is managed via Terraform.
* **Reproducibility:** Every component—from S3 buckets and Lambda functions to OpenSearch Serverless collections—is defined in declarative .tf files.
* **Security Configuration:** Terraform is used to manage strict IAM roles and policies, ensuring the "Principle of Least Privilege" is applied to the data redaction pipeline.
* **Scalability:** By using Terraform modules, we can quickly scale the Bedrock Knowledge Bases and vector indices as the volume of processed medical documents grows.
#### Core AWS Services
* **AWS Bedrock:** Provides access to high-performance models like Claude Sonnet and Nova Pro via a serverless API, reducing the overhead of managing specialized AI hardware.
* **OpenSearch Serverless:** Serves as our vector database, storing embeddings of patient reports for sub-second retrieval during the RAG phase.
* **Lambda & S3 Event Notifications:** Automates the lifecycle of a document; the moment a PDF hits the `/INPUT` bucket, a Lambda triggers the redaction and subsequent ingestion jobs.
* **Comprehend Medical:** An NLP service specifically tuned to detect Protected Health Information (PHI) within clinical text, forming the backbone of our HIPAA compliance strategy.

