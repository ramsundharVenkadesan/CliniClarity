from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import RAG, REACT
import logging
import firebase_admin
from firebase_admin import credentials

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

load_dotenv()
clini_clarity = FastAPI()

cred = credentials.Certificate("/Users/ram/Downloads/CliniGraph/cliniclarity-ec517-firebase-adminsdk-fbsvc-262c38dfa9.json")
firebase_admin.initialize_app(cred)


templates = Jinja2Templates(directory="templates")

clini_clarity.include_router(router=RAG.rag_router)
clini_clarity.include_router(router=REACT.react_router)

@clini_clarity.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )

@clini_clarity.get('/health_check')
async def health_check(): return {'status': "healthy"}

@clini_clarity.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@clini_clarity.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})