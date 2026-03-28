# CliniClarity 🩺

CliniClarity is a patient portal that turns complex medical reports into clear, easy-to-understand health insights using advanced AI (RAG, LangGraph, and a ReAct Agent). It enforces strict HIPAA 'Minimum Necessary' standards and includes a built-in hallucination audit step (via DeepEval) to ensure clinical grounding.

## 🚀 How to Run the App Locally

Follow these steps to set up and run the CliniClarity application on your local machine.

### Prerequisites

You will need the following installed on your machine:
*   **Python 3.10+**
*   **Git**

### Step 1: Clone the Repository
If you haven't already, clone or download this project to your local machine.
```bash
git clone <your-repo-url>
cd CliniGraph
```

### Step 2: Set up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

### Step 3: Install Dependencies
Install all the required Python packages from the requirements file.
*(Note: Ensure you have a `requirements.txt` file generated. If not, install the core libraries manually as listed below).*
```bash
pip install fastapi uvicorn python-multipart jinja2 starlette markdown
pip install langchain langchain-core langchain-google-genai langchain-community
pip install langchain-pinecone pinecone-client
pip install langgraph presidio-analyzer presidio-anonymizer
pip install deepeval pymupdf tavily-python
pip install python-dotenv certifi
```
*(If you are running Presidio for the first time, you may also need to download the SpaCy model it relies on: `python -m spacy download en_core_web_lg`)*

### Step 4: Configure Environment Variables
You need API keys for Google GenAI, Pinecone, and Tavily (for web search), as well as LangSmith (optional, for tracing).

1.  Open the `.env` file in the root directory (or create one).
2.  Fill in your specific API keys:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
INDEX_NAME=your_pinecone_index_name
PINECONE_API_KEY=your_pinecone_api_key
TAVILY_API_KEY=your_tavily_api_key

# Optional LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY="your_langsmith_api_key"
LANGCHAIN_PROJECT="CliniClarity-Dev"

# Disable DeepEval Telemetry (Recommended)
DEEPEVAL_TELEMETRY_OPT_OUT=YES
```
*Note: Make sure your Pinecone index is set up with a dimensionality of 1536 to match the `gemini-embedding-001` model.*

### Step 5: Run the FastAPI Server
You can now start the application using `uvicorn`, pointing it to the FastAPI instance (`clini_clarity`) in `API.py`.

```bash
uvicorn API:clini_clarity --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Use the App
1.  Open your web browser and go to: **[http://localhost:8000](http://localhost:8000)**
2.  You will see the CliniClarity upload page. 
3.  Upload a medical PDF report.
4.  (Optional) Toggle the "DeepEval Security Audit" to run the hallucination check.
5.  Click "Analyze My Report" and watch the pipeline stream in real-time.

## 🏗️ Architecture Overview
*   **Frontend:** HTML/TailwindCSS (Vanilla JS, Server-Sent Events).
*   **Backend:** FastAPI.
*   **Ingestion & Summarization (`RAG.py` & `Agent/RAG_Graph`):** A LangGraph state machine that loads PDFs, redacts PII using Microsoft Presidio, vectorizes chunks into Pinecone, and summarizes the text.
*   **Quality Audit (`Agent/Quality/Hallucination.py`):** Uses DeepEval's `FaithfulnessMetric` to ensure the AI summary is strictly grounded in the uploaded report.
*   **Medical Assistant (`REACT.py` & `Agent/Queries.py`):** A LangChain ReAct agent that answers follow-up questions using the Pinecone vector store and Tavily search (for PubMed medical journals).
