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
flowchart TD
    Start([User Access]) --> Home[Home Page<br/>upload.html]
    
    Home --> Upload{Upload PDF}
    Home --> Question{Ask Question}
    
    Upload --> RAG[RAG Pipeline<br/>RAG.py]
    Question --> ReACT[ReACT Agent<br/>ReACT.py]
    
    RAG --> LoadPDF[Load PDF<br/>PyMuPDFLoader]
    LoadPDF --> Redact[PII Redaction<br/>Redaction.py]
    
    Redact --> Presidio[Presidio Analyzer<br/>& Anonymizer]
    Presidio --> RedactedDoc[Redacted Document<br/>PERSON, PHONE, EMAIL, etc.]
    
    RedactedDoc --> Split[Text Splitting<br/>RecursiveCharacterTextSplitter]
    Split --> Embed[Generate Embeddings<br/>Google Gemini Embedding]
    Embed --> Store[Store in Vector DB<br/>Pinecone]
    
    Store --> Retrieve[Retrieve Context<br/>k=3 chunks]
    Retrieve --> LLM1[LLM Processing<br/>Gemini Flash]
    LLM1 --> Template[Medical Summary Template<br/>6th-grade reading level]
    Template --> Report[HTML Report<br/>report.html]
    
    ReACT --> Tools{Agent Tools}
    Tools --> RetrieverTool[Retriever Tool<br/>Search Patient Report]
    Tools --> TavilyTool[Tavily Search<br/>PubMed Medical Info]
    
    RetrieverTool --> VectorStore[Pinecone Vector Store<br/>Patient's Report]
    TavilyTool --> PubMed[PubMed Database<br/>Medical Literature]
    
    VectorStore --> AgentLLM[ReACT Agent Loop<br/>Gemini Flash]
    PubMed --> AgentLLM[ReACT Agent Loop<br/>Gemini Flash]
    
    AgentLLM --> Think[Thought]
    Think --> Action[Action]
    Action --> Observe[Observation]
    Observe --> Decide{Final Answer?}
    Decide -->|No| Think
    Decide -->|Yes| Answer[Patient-Friendly Answer<br/>6th-grade level]
    
    Report --> End([User Views Summary])
    Answer --> End
    
    style RAG fill:#0066cc,stroke:#003366,stroke-width:3px,color:#fff
    style ReACT fill:#ff8800,stroke:#cc6600,stroke-width:3px,color:#fff
    style Redact fill:#cc0000,stroke:#990000,stroke-width:3px,color:#fff
    style LLM1 fill:#009900,stroke:#006600,stroke-width:3px,color:#fff
    style AgentLLM fill:#009900,stroke:#006600,stroke-width:3px,color:#fff
    style Presidio fill:#cc0000,stroke:#990000,stroke-width:3px,color:#fff
