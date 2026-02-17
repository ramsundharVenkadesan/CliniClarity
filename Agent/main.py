from operator import itemgetter
import markdown
from fastapi.responses import HTMLResponse

from fastapi import FastAPI, File, UploadFile, Response, HTTPException, Request
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel
from starlette import status
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
import io, os, tempfile
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from starlette.templating import Jinja2Templates

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

load_dotenv()
application = FastAPI()
templates = Jinja2Templates(directory="templates")


# Initialize the engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def redact_pii(text: str) -> str:
    # 1. Analyze the text for PII entities (Name, Phone, Email, Location, etc.)
    results = analyzer.analyze(text=text, entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION", "DATE_TIME"],
                               language='en')

    # 2. Anonymize the identified entities
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )
    return anonymized_result.text

@application.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    This endpoint serves a simple upload form.
    When you use this instead of Swagger, the results will show your Jinja2 UI.
    """
    return templates.TemplateResponse("upload.html", {"request": request})

@application.post('/process-pdf/', status_code=status.HTTP_201_CREATED)
async def upload_file(request:Request, file:UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File extension not supported")
    else:
        try:
            pdf_bytes = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_bytes)
                pdf_path = temp_file.name
            try:
                loader = PyMuPDFLoader(pdf_path)
                documents = loader.load()
                print("--- [DEMO] ORIGINAL TEXT FROM PDF ---")
                print(documents[0].page_content[:500])  # Show the first 500 chars with names/dates
                for doc in documents:
                    doc.page_content = redact_pii(doc.page_content)
                print("\n--- [DEMO] REDACTED TEXT (SENT TO PINECONE) ---")
                print(documents[0].page_content[:500])  # Show the same section with [PERSON] tags
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)


            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(documents)


            embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001",
                                                            output_dimensionality=1536,
                                                            google_api_key=os.environ.get("GOOGLE_API_KEY"))
            vector_store = PineconeVectorStore(embedding=embeddings_model, index_name=os.environ.get("INDEX_NAME"))

            vector_store.delete(delete_all=True)

            PineconeVectorStore.from_documents(chunks, embeddings_model, index_name=os.environ.get("INDEX_NAME"))

            retriever_object = vector_store.as_retriever(search_kwargs={"k": 3})

            model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.0)

            medical_summary_template = """
            SYSTEM: You are a compassionate Patient Advocate and Health Literacy Expert. 
            Your goal is to explain a complex medical report to someone with NO medical background. 

            CLINICAL CONTEXT: 
            {context}

            USER QUERY: 
            {query}

            INSTRUCTIONS for Accessibility:
            - Use a 6th-grade reading level. 
            - Avoid medical jargon. If you must use a term (e.g., 'Spiculated'), explain it simply (e.g., 'spiky or irregular shape').
            - Use the 'What, So What, Now What' framework.
            - Use emojis to make the report less intimidating.

            # 🩺 Your Health Summary (Simplified)
            ---
            ## 💡 The Main Takeaway (The 'What')
            [Provide a 2-sentence summary using everyday language. Example: 'The doctors found a spot on your lung that needs more testing right away.']

            ## 🔍 What the Results Mean (The 'So What')
            - **The Finding:** [Explain the primary issue without using scary jargon unless defined.]
            - **Why it matters:** [Explain why the doctor is concerned in a calm, supportive way.]

            ## 📊 Key Labs & Vitals
            [Only list the most important ones. Explain 'High' or 'Low' instead of just numbers.]
            - **Blood Sugar:** [Explain it like: 'Higher than normal, which means your diabetes needs more attention.']

            ## 🚶 Your Next Steps (The 'Now What')
            1. **Priority 1:** [Most urgent action]
            2. **Priority 2:** [Next follow-up]

            ## ❓ Questions for your Doctor
            [Provide 2 questions the patient can literally read out loud to their doctor at the next visit.]

            ---
            *Disclaimer: This is an AI-generated summary to help you understand your report. Please discuss all findings with your healthcare team.*
            """

            prompt_template = ChatPromptTemplate.from_template(template=medical_summary_template)

            def format_documents(documents):
                return "\n\n".join(document.page_content for document in documents)

            def retrieval_chain():
                chain = RunnablePassthrough.assign(context=itemgetter(
                    'query') | retriever_object | format_documents) | prompt_template | model | StrOutputParser()
                return chain

            response = retrieval_chain().invoke({'query': "Summarize the report"})
            html_content = markdown.markdown(response)

            return templates.TemplateResponse("report.html", {
                "request": request,
                "summary_html": html_content,
                "chunks": len(chunks),
                "sources": 1
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


