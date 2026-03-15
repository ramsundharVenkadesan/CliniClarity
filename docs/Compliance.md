# Compliance & Data Privacy: HIPAA Framework
CliniClarity is built with a "Privacy by Design" philosophy, ensuring that patient trust is maintained through rigorous automated security protocols and high-authority data grounding

---

## PHI & PII Safeguards (The Redaction Pipeline)
To ensure that sensitive information is never leaked to public Large Language Models (LLMs) or used for training, we implement a multi-stage sanitization pipeline.
* **Localized Redaction:** Every uploaded document is processed by Microsoft Presidio. Unlike cloud-based PII services, this engine runs natively on our EC2 nodes, identifying 18+ types of Protected Health Information (PHI) including names, MRNs, and contact details before any data is vectorized.
* **Irreversible Scrubbing:** Once identified, the PHI is scrubbed from the text in-memory. This ensure that only the anonymized clinical context is passed to the embedding engine, effectively creating a "Safe Harbor" for patient data.
* **Memory-Only Processing:** Raw, unredacted text is never written to persistent storage in a searchable format; it exists only in a transient state during the redaction phase.

---

## Technical Safeguards (AWS Infrastructure)
The infrastructure is designed to physically and logically separate sensitive ingestion from the reasoning environment.
* **VPC Isolation:** All reasoning and redaction nodes are isolated within Private Subnets with zero public ingress. All external traffic is routed through a central Application Load Balancer (ALB) and a NAT Gateway, providing a single, auditable point of egress.
* **Vector Security:** Sanitized clinical embeddings are stored in Pinecone. Access is controlled via strictly scoped API keys and IAM roles, ensuring that the "Principle of Least Privilege" is applied to the data retrieval layer.
* **Encryption at Rest & In-Transit:** All data is encrypted at rest using AES-256 (EBS volumes and Pinecone indices) and in-transit via TLS 1.2+ for all API communication with Gemini and PubMed

---

## Clinical Safety & Hallucination Mitigation
Beyond data privacy, "Compliance" in medical PLM includes the safety and accuracy of the information provided to the user.
* **Grounded RAG:** The LangGraph engine is restricted to providing answers found only in the provided records or vetted clinical journals.
* **Automated Auditing:** We utilize **DeepEval** as a deterministic clinical auditor. Every response is measured for "Faithfulness" and "Answer Relevancy" against the source document. If a response fails these metrics, the state machine triggers a self-correction loop.
* **Non-Diagnostic Intent:** The system is explicitly engineered as a "Research Librarian," prioritizing evidence-based education over diagnostic prescription.

## Auditability & Transparency
Transparency ensures that every claim made by the AI can be verified by a human healthcare professional.
* **Direct Citations:** Every summary statement is linked to a specific line in the patient's record or a specific DOI (Digital Object Identifier).
* **Source Verification:** This allows patients to bring evidence-based questions to their doctors, facilitating more productive and efficient consultations
