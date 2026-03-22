# Architecture Decision Record: Real-time Prompt Security with Protect AI Guardian

* **Status:** Accepted
* **Date:** 2026-03-22

## Context
As CliniClarity moves toward production, the risk of Prompt Injection (LLM01) and accidental Sensitive Information Disclosure (LLM06) poses a significant threat to our security posture. In a healthcare context, a malicious or accidental input that bypasses safety filters could lead to unauthorized data access or the bypass of medical guardrails. We need a high-performance, scalable solution to audit prompts before they reach the core LLM logic.

## Decision: Implement Protect AI Guardian as the Primary Security Gateway
We have integrated Protect AI Guardian to serve as the "security perimeter" for the CliniClarity LangGraph workflow. Every user-entered prompt must pass through the Guardian gateway before being processed by the Gemini model.

## Decision Rationale
* **Latency-Optimized Security:** Unlike "evaluator-model" frameworks that require a second LLM call, Protect AI Guardian provides sub-millisecond evaluation, which is critical for maintaining the responsive UI required for medical professional tools.
* **Automated PHI Redaction:** It provides native, real-time scrubbing of Protected Health Information (PHI) and PII, ensuring that sensitive patient identifiers never reach the LLM provider, directly supporting our HIPAA compliance goals.
* **Proactive Threat Intelligence:** By leveraging the Huntr vulnerability community, the system is protected against the latest jailbreak and bypass techniques that standard regex or manual "math" approaches cannot detect.
* **Enterprise Scaling:** The solution is significantly more cost-effective than per-token cloud-native filters, allowing CliniClarity to scale without a linear increase in security overhead.

## Alternative Considered 
* **Manual Regex/Math Evaluation:** This approach was initially tested but proved to be unscalable and brittle. It struggled with semantic escapes—where users rephrase malicious intent to bypass keyword filters—and created a high maintenance burden for the engineering team.
* **Cloud-Native Guardrails (e.g., AWS Bedrock/Azure AI):** While robust, these solutions often function as "black boxes" with higher network latency and pricing models that are less predictable for high-volume healthcare applications. They also lacked the deep integration with the open-source security community (like Huntr) that Protect AI provides.
