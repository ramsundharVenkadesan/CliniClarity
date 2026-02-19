# 📂 Agent Module: Reasoning & Retrieval Engine

This directory contains the autonomous reasoning core for CliniClarity. It is architected to handle complex medical queries by dynamically selecting between internal patient data and verified external medical literature.

## 🏗️ Architecture Overview
* **Logic Engine:** Implements the **ReACT (Reason + Act)** pattern using LangChain and Gemini-3-Flash.
* **Privacy Guard:** Integrated **Microsoft Presidio** pipeline (`Redaction.py`) ensures that no PII (Personally Identifiable Information) is processed by the LLM reasoning loop.
* **Dual-Tool Strategy:**
    * **Internal:** `clini_clarity_docs` (Pinecone Vector Store) for patient-specific context.
    * **External:** `Tavily Search` (Restricted to PubMed) for general medical grounding.

## 📑 Key Components
* **`ReACT.py`**: The main entry point for agent logic and tool definition.
* **`Redaction.py`**: A privacy utility used to sanitize input strings before they enter the vector or reasoning streams.

## 🧪 Implementation Standards (PLM)
1.  **Safety First:** Uses `handle_parsing_errors=True` to maintain agent stability during complex multi-step reasoning.
2.  **Persona-Driven:** The system prompt enforces a "Patient Advocate" persona to ensure empathetic and accessible communication.
3.  **Accuracy-Focused:** Search tools are restricted to reputable clinical domains to prevent "hallucinations" based on non-medical sources.

4.  ## 🏗️ Architecture Overview

```mermaid
graph LR
    %% Entry Point
    Input((User Question)) --> Agent[ReACT Agent Logic<br/>ReACT.py]

    subgraph "Privacy & Pre-processing"
        Agent -.-> Redactor[Redaction Logic<br/>Redaction.py]
        Redactor --> Presidio[Presidio Analyzer/Anonymizer]
        Presidio -.-> |Scrubbed Context| Agent
    end

    subgraph "Reasoning Loop (Thought-Action-Observation)"
        Agent --> Choice{Tool Choice}
        
        %% Internal Path
        Choice -->|Internal Data| RetTool[Retriever Tool]
        RetTool --> Pinecone[(Pinecone Vector Store)]
        Pinecone -->|Redacted Medical Facts| Obs1[Observation]
        
        %% External Path
        Choice -->|Medical Validation| SearchTool[Tavily Search]
        SearchTool --> PubMed[NCBI/PubMed Domains]
        PubMed -->|External Context| Obs2[Observation]
    end

    %% Final Output
    Obs1 --> Agent
    Obs2 --> Agent
    Agent -->|Gemini-3-Flash| Final[6th-Grade Level Summary]
    Final --> Output((Final Answer))

    style Agent fill:#f9f,stroke:#333,stroke-width:2px
    style Redactor fill:#bbf,stroke:#333
