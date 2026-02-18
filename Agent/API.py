from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from RAG import rag_router
from ReACT import router as question_router

# 1. Load Environment Variables before importing anything else
load_dotenv()

# 2. Initialize App
application = FastAPI()

# 3. Initialize Templates (For the home page)
templates = Jinja2Templates(directory="templates")

# 4. Mount Routers
# This connects the logic from RAG.py and ReACT.py to the main app
application.include_router(rag_router)
application.include_router(question_router)

@application.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serves the upload form.
    """
    return templates.TemplateResponse("upload.html", {"request": request})



