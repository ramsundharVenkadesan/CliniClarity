This document outlines the validation strategies used to ensure the security, reliability, and medical accuracy of CliniClarity.

# 1. LLM Evaluation (DeepEval)
We utilize **DeepEval** to perform "Unit Testing" on the AI's output. The primary metric is the **Faithfulness Metric**, which measures how well the summary is grounded in the original medical context.
* **Threshold:** Score > 0.9 (Accepted); Score ≤ 0.9 (Rejected).
* **Audit Process:** If a summary falls below the threshold, the system flags a potential hallucination and rejects the state update.

---

# 2. Security & Compliance Testing
* **Prompt Injection Scanning:** We test the **ProtectAI** (DeBERTa-v3) classifier against adversarial benchmarks to ensure a confidence score of at least 0.8 for blocking malicious input.
* **Medical Document Gatekeeper:** A specialized **Gemini**-backed validation node ensures the system only processes medical files, requiring a confidence score >0.8 to pass the initial gate.
* **PII Scrubbing Validation:** Manual and automated tests confirm that **Microsoft Presidio** successfully masks the 18 specific identifiers required for HIPAA "Safe Harbor" compliance.

---

# 3. Infrastructure & Deployment Testing
* **Static IaC Analysis:** Every infrastructure change is preceded by a `terraform plan` to identify configuration drift or security misconfigurations.
* **Purge Verification:** On every `terraform destroy`, a specialized `Purge_Users.py` script is triggered to verify that all user identities and data namespaces are wiped from the backend.

---

# 4. Application Logic Tests
* **Streaming Integrity:** Testing the Server-Sent Events (SSE) pipeline to ensure the UI correctly interprets `type: status` and `type: complete` messages during long-running agent tasks.
* **Cold-Start Performance:** Monitoring the effectiveness of `startup_cpu_boost` and global client initialization to keep initial request latency under acceptable thresholds.
