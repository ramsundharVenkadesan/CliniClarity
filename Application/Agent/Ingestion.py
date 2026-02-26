from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from typing import Optional, List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv
load_dotenv()

embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", output_dimensionality=1536, google_api_key=os.environ.get("GOOGLE_API_KEY"))
vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))


async def redact_data(text:str, entities: Optional[List[str]] = None) -> str:
    results = AnalyzerEngine().analyze(text=text, entities=entities, language="en")
    anonymizer = AnonymizerEngine().anonymize(text=text, analyzer_results=results)
    return anonymizer.text

async def ingestion(file_path:str) -> List:
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()

        print(docs[0].page_content[:500])

        for document in docs:
            document.page_content = await redact_data(document.page_content)

        print(docs[0].page_content[:500])

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        vector_database.delete(delete_all=True)

        PineconeVectorStore.from_documents(documents=chunks, embedding=embedding_model, index_name=os.environ.get("INDEX_NAME"))

        return [True, chunks]
    except Exception as e:
        print(e)
        return False






