# Architecture Decision Record: LLM Selection for Medical Summarization and Q&A

* **Status:** Accepted
* **Date:** 2026-03-22

## Context
CliniClarity requires a core LLM engine to perform two critical tasks: summarizing complex medical reports and answering patient queries with high precision. In a healthcare environment, the engine must not only be accurate but also provide structured outputs (JSON/Schema) that can be reliably parsed by the downstream PII redaction (Microsoft Presidio) and hallucination auditing (DeepEval) layers.

## Decision: Implement `gemini-3-flash-preview` as the Primary Reasoning Engine
We have selected `gemini-3-flash-preview` to serve as the "brain" of the CliniClarity agentic workflow.
