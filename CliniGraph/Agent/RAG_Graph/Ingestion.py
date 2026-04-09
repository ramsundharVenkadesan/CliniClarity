import datetime # Import Date-Time module
import hashlib # Import Hashing Library
import os # Import OS module
from langchain_text_splitters import RecursiveCharacterTextSplitter # Import class to split documents into chunks
from langchain_community.document_loaders import PyMuPDFLoader # Import class to load the input PDF document
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Import class to convert chunks into embeddings
from langchain_pinecone import PineconeVectorStore # Import class to store the embeddings in a vector space
from dotenv import load_dotenv # Import function to load environment variables
from presidio_analyzer import AnalyzerEngine # Import class to analyze the input PDF document for PHI and PII
from presidio_anonymizer import AnonymizerEngine # Import class to redact the analyzed fields in the document
from Agent.RAG_Graph.State import GraphState # Import class to store state between each node
from typing import Dict, Any # Import Type-Hints package
from pathlib import Path # Import Path library

current_dir = Path(__file__).parent # Get current directory
ACTIVITY_LOG_FILE = current_dir.parent.parent / "activity.log" # Go two levels up the order to access the logging file

load_dotenv() # Invoke function to load all the API keys
SUMMARY_CACHE = {} # Local Caching Dictionary

embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", # Embedding model developed by Google
                                               output_dimensionality=1536, # Dimensionality of the embedding
                                               google_api_key=os.environ.get("GOOGLE_API_KEY")) # Gemini API key

vector_database = PineconeVectorStore(embedding=embedding_model, index_name=os.environ.get("INDEX_NAME")) # Create an instance representing a Pinecone vector database


async def load_pdf(state:GraphState) -> Dict[str, Any]: # Node that accepts the current state and loads the PDF documents
    loader = PyMuPDFLoader(state['file_path']) # Load the PDF document into the Document-Loader class
    docs = loader.load() # Load the PDF file into LangChain Documents
    raw_pdf_text = "".join([doc.page_content for doc in docs]) # Combined raw text data from each loaded document

    doc_hash = hashlib.md5(raw_pdf_text.encode('utf-8')).hexdigest() # Create a MD5 hash of the raw text

    if doc_hash in SUMMARY_CACHE: # Check if the hash is in the dictionary
        with open(ACTIVITY_LOG_FILE, mode='a', encoding='utf-8') as logging_file: # Open logging file in append mode
            print(f"[{datetime.datetime.now()}] --- ♻️ CACHE HIT: Duplicate Document Detected ---", file=logging_file) # Write cache hit to the logging file

        return { # Return a dictionary object
            'documents': docs, # The loaded documents
            'pdf_text': raw_pdf_text, # Raw PDF text
            'summary': SUMMARY_CACHE[doc_hash],  # Retrieve the old summary from memory
            'is_cached': True  # Flag to tell the router to skip ingestion and generation
        }

    return {'documents': docs, 'pdf_text': raw_pdf_text, 'doc_hash': doc_hash, 'is_cached': False} # Update the state dictionary with the loaded document


async def redact_PII(state:GraphState) -> Dict[str, Any]: # Node to redact the load documents
    docs = state.get('documents') # Retrieve the list of loaded documents from state-dictionary

    analyzer = AnalyzerEngine() # Initialize Presidio-Analyzer to identify any PII or PHI data
    anonymizer = AnonymizerEngine() # Initialize the Presidio Anonymizer to mask the identified data

    for document in docs: # Iterate through the retrieved documents
        results = analyzer.analyze(text=document.page_content, language='en') # Analyze each document's content
        anonymized = anonymizer.anonymize(text=document.page_content, analyzer_results=results) # Redact the identified data
        document.page_content = anonymized.text # Update the document's content with redacted text

    return {'documents': docs} # Update the state-dictionary with redacted documents


async def ingestion(state:GraphState) -> Dict[str, Any]: # Node to inject redacted documents to Pinecone

    try: # Attempt to connect and ingest chunks into Pinecone

        cleaned_docs = state.get('documents') # Retrieve the list of redacted documents from state-dictionary
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) # Text-Splitter to split the documents into chunks
        chunks = splitter.split_documents(cleaned_docs) # Split the redacted documents into chunks

        try: # Attempt to clear any existing chunks from the database
            vector_database.delete(delete_all=True) # Delete or clean any existing chunks in the vector-database
        except Exception as delete_error: # Error in deleting existing chunks in the vector-database
            print(f"Skipped deletion (index likely empty). Details: {delete_error}") # Index is empty

        PineconeVectorStore.from_documents(documents=chunks, embedding=embedding_model, index_name=os.environ.get("INDEX_NAME")) # Initialize a vector-database with chunks and embedding model
        return {'documents': chunks, 'status': True} # Update the state dictionary with loaded chunks and status to true because ingestion was successful

    except Exception as e: # Exception block to catch any ingestion errors
        with open(ACTIVITY_LOG_FILE, mode="a") as file: # Open the Log-File in append mode
            file.write(f"[{datetime.datetime.now()}] Ingestion Error: {e}\n") # Write the ingestion error to the file
        return {'status': False} # Update status-property to False because ingestion failed



