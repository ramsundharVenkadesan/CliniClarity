# Compliance & Data Privacy: HIPAA Framework
CliniClarity is built with a "Privacy by Design" philosophy, ensuring that patient trust is maintained through rigorous automated security protocols and high-authority data grounding

## PHI & PII Safeguards (The Redaction Pipeline)
To ensure that sensitive information is never leaked to public Large Language Models (LLMs) or used for training, we implement a multi-stage sanitization pipeline.
* **Detection:** Every uploaded document is processed by AWS Comprehend Medical, which is specifically trained to identify medical-specific entities like Medical Record Numbers (MRN), patient names, and dates.
* **Coordinate Mapping:** We utilize AWS Textract to create bounding boxes with exact spatial coordinates (x, y, width, height) for every word on the document.
* **Irreversible Redaction:** A Lambda function matches identified PHI to these coordinates and uses the ReportLab library to draw solid black boxes over the text.
* **Metadata Stripping:** The underlying text metadata is removed from the PDF, ensuring it cannot be searched or "highlighted" underneath the box.

## Technical Safeguards (AWS Infrastructure)
Our infrastructure is designed to separate "raw" patient data from the "searchable" context used by the AI agent.
* **Siloed Storage:** Raw documents are stored in an encrypted `/INPUT` S3 bucket with restricted IAM roles.
* **Vector Isolation:** Only the sanitized (redacted) PDF is sent to the `/OUTPUT bucket` for chunking into OpenSearch Serverless.
* **In-Transit Encryption:** All data movement between Lambda, S3, Bedrock, and OpenSearch is encrypted using TLS 1.2 or higher.

## Clinical Safety & Hallucination Mitigation
Beyond data privacy, "Compliance" in medical PLM includes the safety and accuracy of the information provided to the user.
* **Grounded RAG:** The model is restricted to providing answers found only in the provided records or vetted journals.
* **The ReAct "Guardrail":** The Thinking -> Action -> Observation loop forces the agent to verify clinical facts against high-authority databases like PubMed before delivering a response.
* **Non-Diagnostic Intent:** The system is explicitly engineered as a research librarian, emphasizing education over prescription to avoid unauthorized medical advice

## Auditability & Transparency
Transparency is key to medical literacy. We ensure that every claim made by the AI can be verified by a human professional.
* **Direct Citations:** Every summary statement is linked to a specific line in the patient's record or a specific DOI (Digital Object Identifier).
* **Source Verification:** This allows patients to bring evidence-based questions to their doctors, facilitating more productive and efficient consultations
