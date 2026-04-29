from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import RAG, REACT
import logging
import firebase_admin
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

load_dotenv()
clini_clarity = FastAPI()

firebase_admin.initialize_app(options={'projectId': 'cliniclarity'})


templates = Jinja2Templates(directory="templates")

clini_clarity.include_router(router=RAG.rag_router)
clini_clarity.include_router(router=REACT.react_router)

def get_firebase_config():
    return {
        "firebase_api_key": os.getenv("FIREBASE_API_KEY"),
        "firebase_auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "firebase_project_id": "cliniclarity" # Hardcoded project ID is safe, or pull from env
    }

@clini_clarity.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return templates.TemplateResponse(request=request, name="privacy.html")

@clini_clarity.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse(request=request, name="terms.html")

@clini_clarity.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    context = {"request": request}
    context.update(get_firebase_config())
    return templates.TemplateResponse(request=request, name="login.html", context=context)
@clini_clarity.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {"request": request}
    context.update(get_firebase_config())
    return templates.TemplateResponse(
        request=request, name="upload.html",
        context=context
    )

@clini_clarity.get('/health_check')
async def health_check(): return {'status': "healthy"}
