# CliniClarity: Security & Compliance Architecture
**Objective:** To establish a deterministic, zero-trust security posture for the processing of medical documents and generation of clinical summaries

---

## Zero-Trust Ingress (Layer 0 & 1)
CliniClarity operates under the assumption that all user input is potentially hostile or irrelevant. We employ a multi-tiered ingress defense mechanism before any data enters the cognitive pipeline.
* **The Medical Gatekeeper (Tier 0):** A two-stage validation process blocks non-clinical data. A fast heuristic scan checks for medical markers, followed by a lightweight LLM validation. If a user uploads a non-medical document (e.g., a recipe or malicious script), the stream is gracefully terminated, preventing vector database pollution and API waste.
* **Local Adversarial Defense (Tier 1):** Before the LangChain orchestrator receives the document, the text is scanned by a localized Hugging Face Small Language Model (ProtectAI DeBERTa). This model acts as a physical firewall, detecting and blocking prompt injections, DAN attacks, and jailbreak attempts with microsecond latency.
* **Prompt Sandboxing:** All extracted clinical text is strictly isolated within XML delimiters (`<clinical_data>`). The agent is explicitly instructed to treat any commands found within these delimiters as untrusted plain text, neutralizing embedded system overrides.

---

## Cognitive Security & Grounding (The AI Orchestrator)
The core reasoning engine (LangGraph) has been heavily modified to prioritize deterministic execution over probabilistic guessing.
* **Native JSON Tool Calling:** We have deprecated legacy text-parsing ReAct frameworks. The agent communicates with tools using strictly typed JSON schemas. This prevents tool hijacking and ensures the agent cannot execute arbitrary code or unauthorized system commands.
* **Objective Hallucination Auditing:** Utilizing DeepEval, every clinical synthesis is objectively scored against the retrieved document context. The system is physically incapable of finalizing a summary if the hallucination threshold is breached.
* **Clinical Verification via FastMCP:** General web search is disabled. When the agent requires external medical verification, it queries the National Library of Medicine (PubMed) via a localized Model Context Protocol (MCP) server running over strictly controlled stdio pipes
* **The Reflection Agent:** A self-correcting cognitive loop audits the draft summary for patient readability and empathetic tone. To prevent infinite loops, this node is strictly capped at a maximum of 3 retries.

---

## Zero-Trust Egress (Data Exfiltration & Safety)
Securing the output is just as critical as securing the input. CliniClarity employs a "Circuit Breaker" architecture to intercept compromised responses.
* **Intrinsic Safety Alignment:** By neutralizing external payload injections at the ingress point (via DeBERTa) and explicitly removing code-execution tools from the reasoning environment, CliniClarity safely leverages the core LLM to generate clinical summaries without requiring a heavy, resource-intensive egress-evaluation model.
* **Double-Pass PII Redaction:** Microsoft Presidio is implemented on both the ingress and egress nodes. It redacts Protected Health Information (PHI) before it is sent to the LLM, and scans the final output to ensure no hallucinations have leaked synthetic or real identifiers.

## Operational Resilience
Transparency ensures that every claim made by the AI can be verified by a human healthcare professional.
* **Semantic Caching:** Redundant queries are intercepted by a local caching layer, significantly reducing API latency and preventing unnecessary token expenditure for standard medical definitions.
* **Graceful SSE Error Handling:** All security intercepts (Ingress blocks, Egress blocks, Validation failures) are natively mapped to Server-Sent Events (SSE). The system never crashes; instead, it streams formatted JSON errors that the frontend gracefully displays to the user.
