from starlette import status
import markdown, tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from starlette.templating import Jinja2Templates
import Agent.Ingestion
import Agent.Retrieval

rag_router = APIRouter(tags=["Summary"], prefix="/summary")
templates = Jinja2Templates(directory="templates")

@rag_router.post("/", status_code=status.HTTP_201_CREATED)
async def generate_summary(request:Request, file:UploadFile):
    if file.filename.endswith(".pdf"):
        try:
            pdf_bytes = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_file:
                temporary_file.write(pdf_bytes)
                pdf_path = temporary_file.name
            ingestion_result = await Agent.Ingestion.ingestion(pdf_path)
            if ingestion_result[0]:
                summary = await Agent.Retrieval.summarize()
                html_markdown = markdown.markdown(summary)
                return templates.TemplateResponse("report.html", {
                    "request": request, "summary_html": html_markdown, "chunks" : len(ingestion_result[1]), "sources": 1
                })
            else:
                raise HTTPException(status_code=500, detail="Error in ingestion")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
