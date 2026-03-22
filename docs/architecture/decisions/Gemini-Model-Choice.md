# Architecture Decision Record: LLM Selection for Medical Summarization and Q&A

* **Status:** Accepted
* **Date:** 2026-02-22

## Context
CliniClarity requires a core LLM engine to perform two critical tasks: summarizing complex medical reports and answering patient queries with high precision. In a healthcare environment, the engine must not only be accurate but also provide structured outputs (JSON/Schema) that can be reliably parsed by the downstream PII redaction (Microsoft Presidio) and hallucination auditing (DeepEval) layers.

## Decision: Implement `gemini-3-flash-preview` as the Primary Reasoning Engine
We have selected `gemini-3-flash-preview` to serve as the "brain" of the CliniClarity agentic workflow.

## Decision Rationale
* **Operational Efficiency & Speed:** The model provides a high "intelligence-to-latency" ratio. For real-time clinical assistants, minimizing the "time-to-first-token" is essential for user trust and utility.
* **Native Structured Output:** Unlike many experimental models, `gemini-3-flash-preview` excels at adhering to strict output schemas. This reliability ensures that medical summaries are returned in a consistent format, preventing application crashes during the data-parsing stage.
* **Cost-Effectiveness:** Building a scalable healthcare solution requires managing operational overhead. This model provides enterprise-grade performance at a fraction of the cost of "larger" flagship models, allowing for higher volume document processing.
* **Reliable Consistency:** During testing, the model demonstrated a "steady-state" behavior—providing consistent answers to identical prompts, which is a prerequisite for clinical safety and auditability.

## Alternatives Considered
* **Local Models (e.g., Llama 3, Mistral):** Evaluated but rejected due to hardware-dependent variability. Inference speed and output quality fluctuated significantly based on the local machine's resources, making it impossible to guarantee a standardized "Quality of Service" (QoS) for a production healthcare application.
* **OpenAI Models (e.g., GPT-4o):** Rejected due to inconsistent output formatting and a higher observed frequency of hallucinations during complex medical summarization. Furthermore, significantly slower response times and higher token costs provided a lower return on investment (ROI) compared to the Flash-tier model.
