import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from Agent.RAG_Graph.State import GraphState

load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=1536, google_api_key=os.environ.get("GOOGLE_API_KEY"))
vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))

async def load_pdf(state:GraphState):
    loader = PyMuPDFLoader(state['file_path'])
    docs = loader.load()
    return {'documents': docs}

async def redact_PII(state:GraphState):
    docs = state['documents']

    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    for document in docs:
        results = analyzer.analyze(text=document.page_content, language='en')
        anonymized = anonymizer.anonymize(text=document.page_content, analyzer_results=results)
        document.page_content = anonymized.text

    return {'documents': docs}

async def ingestion(state:GraphState):
    try:
        cleaned_docs = state['documents']
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(cleaned_docs)
        vector_database.delete(delete_all=True)
        PineconeVectorStore.from_documents(documents=chunks, embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))
        return {'documents':chunks, 'status': True}
    except Exception as e:
        print(f"Ingestion Error: {e}")
        return {'status': False}



