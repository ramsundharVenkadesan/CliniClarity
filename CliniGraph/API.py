import os
from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
load_dotenv()

import Feedback
clini_clarity = FastAPI()

templates = Jinja2Templates(directory="templates")

# Only load RAG/REACT routers if API keys are configured
if os.environ.get("GOOGLE_API_KEY"):
    import RAG, REACT
    clini_clarity.include_router(router=RAG.rag_router)
    clini_clarity.include_router(router=REACT.react_router)

clini_clarity.include_router(router=Feedback.feedback_router)

@clini_clarity.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )
