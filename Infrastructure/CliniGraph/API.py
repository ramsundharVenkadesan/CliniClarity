from fastapi import FastAPI, Request # Import classes from FastAPI package
from starlette.templating import Jinja2Templates # Import class to render HTML files
from fastapi.responses import HTMLResponse # Import class to parse response to HTML files
from dotenv import load_dotenv # Import class to load environment variables
import RAG, REACT # Import RAG and ReACT routers
import logging # Import logging package
import firebase_admin # Import Firebase Admin package
import os # Import OS package

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s") # Configure logging framework

load_dotenv() # Load all API keys required to run the infrastructure
clini_clarity = FastAPI() # Instance required to start up FastAPI server
firebase_project_id = os.getenv("FIREBASE_PROJECT_ID") # Retrieve Firebase Project
firebase_admin.initialize_app(options={'projectId': firebase_project_id}) # Initialize Firebase using the project

templates = Jinja2Templates(directory="templates") # Instance to render all HTML files

clini_clarity.include_router(router=RAG.rag_router) # Connect RAG API Router
clini_clarity.include_router(router=REACT.react_router) # Connect ReACT API Router

def get_firebase_config(): # Function to retrieve firebase configuration
    return { # A dictionary object with Firebase attributes
        "firebase_api_key": os.getenv("FIREBASE_API_KEY"), # Firebase API key retrieved from environment variable
        "firebase_auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN"), # Firebase Auth-Domain retrieved from environment variable
        "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID") # Firebase Project ID retrieved from environment variable
    }

@clini_clarity.get("/privacy", response_class=HTMLResponse) # Get Request to retrieve privacy policy
async def privacy_page(request: Request): return templates.TemplateResponse(request=request, name="privacy.html") # Render Privacy HTML file

@clini_clarity.get("/terms", response_class=HTMLResponse) # Get Request to retrieve terms policy
async def terms_page(request: Request): return templates.TemplateResponse(request=request, name="terms.html") # Render Terms HTML file

@clini_clarity.get("/login", response_class=HTMLResponse) # Get Request to retrieve login page
async def login_page(request: Request): # Asynchronous function to render login page and accept user credentials
    context = {"request": request} # Wrap request into a dictionary
    context.update(get_firebase_config()) # Update the dictionary with Firebase configuration
    return templates.TemplateResponse(request=request, name="login.html", context=context) # Render page with request and Firebase configuration
@clini_clarity.get("/", response_class=HTMLResponse) # Get Request to retrieve upload page
async def index(request: Request): # Asynchronous function to render upload page
    context = {"request": request} # Wrap request into a dictionary
    context.update(get_firebase_config()) # Update the dictionary with Firebase configuration
    return templates.TemplateResponse(request=request, name="upload.html", context=context) # Render page with request and Firebase configuration

@clini_clarity.get('/health_check') # Get Request to ensure application is healthy
async def health_check(): return {'status': "healthy"} # Dictionary to indicate function is healthy
