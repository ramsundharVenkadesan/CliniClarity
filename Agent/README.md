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

## 🏗️ System Architecture

```mermaid
graph TD
    %% User Interaction
    User((User)) -->|Upload PDF| API[API.py / FastAPI]
    User -->|Ask Question| API

    subgraph "Ingestion & Privacy Layer"
        API -->|Route: /rag/process-pdf| RAG_Router[RAG.py]
        RAG_Router -->|Raw Text| Redactor[Redaction.py / Presidio]
        Redactor -->|Analyzes PII| Analyzer[AnalyzerEngine]
        Analyzer -->|Anonymizes| Anonymizer[AnonymizerEngine]
        Anonymizer -->|Scrubbed Text| Splitter[RecursiveCharacterTextSplitter]
    end

    subgraph "Vector Storage"
        Splitter -->|Chunks| Embed[Gemini-Embedding-001]
        Embed -->|Vectors| Pinecone[(Pinecone Vector Store)]
    end

    subgraph "Reasoning & Retrieval Layer"
        API -->|Route: /question/| ReACT[ReACT.py / Agent]
        ReACT -->|Thought/Action| Selector{Agent Executor}
        
        Selector -->|Action 1| RetTool[Retriever Tool]
        RetTool -->|Search| Pinecone
        
        Selector -->|Action 2| SearchTool[Tavily Search]
        SearchTool -->|External Search| PubMed[PubMed/NCBI]
        
        Selector -->|Observation| LLM[Gemini-3-Flash]
    end

    %% Final Output
    LLM -->|Final Answer: 6th Grade Level| Response[User Health Summary]
    Response --> User

    %% High-Contrast Styling
    style ReACT fill:#f0f0f0,stroke:#333,stroke-width:2px
    style Redactor fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style API fill:#ffffff,stroke:#333
