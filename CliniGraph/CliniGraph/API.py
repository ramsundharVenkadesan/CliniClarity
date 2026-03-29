from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

import Feedback

rag_import_error = None
react_import_error = None

try:
    import RAG
except Exception as exc:
    RAG = None
    rag_import_error = str(exc)

try:
    import REACT
except Exception as exc:
    REACT = None
    react_import_error = str(exc)

clini_clarity = FastAPI()


templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

clini_clarity.include_router(router=Feedback.feedback_router)

if RAG is not None:
    clini_clarity.include_router(router=RAG.rag_router)

if REACT is not None:
    clini_clarity.include_router(router=REACT.react_router)

@clini_clarity.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if RAG is None or REACT is None:
        missing_components = []
        if rag_import_error is not None:
            missing_components.append(f"summary pipeline unavailable: {rag_import_error}")
        if react_import_error is not None:
            missing_components.append(f"question pipeline unavailable: {react_import_error}")

        return HTMLResponse(
            content=(
                "<html><body style=\"font-family: sans-serif; padding: 2rem; max-width: 52rem; margin: 0 auto;\">"
                "<h1>CliniClarity</h1>"
                "<p>The feedback microservice is available, but the AI app is not fully installed yet.</p>"
                f"<p>{'<br>'.join(missing_components)}</p>"
                "<p>Test feedback with:</p>"
                "<pre>POST /feedback/experience\nGET /feedback/experience/summary</pre>"
                "<p>Once the AI dependencies are installed, this page will return to the normal upload UI.</p>"
                "</body></html>"
            )
        )

    return templates.TemplateResponse(request, "upload.html", {"request": request})
