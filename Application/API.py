from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
load_dotenv()
import REACT, RAG


clini_clarity = FastAPI()
templates = Jinja2Templates(directory="templates")

clini_clarity.include_router(router=RAG.rag_router)
clini_clarity.include_router(router=REACT.react_router)

@clini_clarity.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )