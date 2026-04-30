import markdown, tempfile, json, os
from fastapi import APIRouter, UploadFile, HTTPException, Request, Form, Depends
from fastapi.responses import StreamingResponse
from starlette.templating import Jinja2Templates
from Agent.RAG_Graph.Workflow import rag_app # Import the complied graph
from pypdf import PdfReader
from Agent.Security.Validation import *
from transformers import pipeline
from google.cloud import storage
from firebase_admin import auth # Added for token verification
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
storage_client = storage.Client()
import logging

security = HTTPBearer()

def verify_token(credentials:HTTPAuthorizationCredentials=Depends(security)):
    """Middleware to verify the user's Firebase JWT."""
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token['uid']  # Returns the unique user ID
    except Exception as e:
        logging.error(f"🚨 FIREBASE AUTH ERROR: {str(e)}")  # <--- ADD THIS LINE
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

rag_router = APIRouter(tags=["Summary"], prefix="/summary")
templates = Jinja2Templates(directory="templates")

ingress_scanner = pipeline(
    "text-classification",
    model="protectai/deberta-v3-base-prompt-injection-v2"
)


async def scan_for_prompt_injection(text: str) -> bool:
    """Scans the uploaded document for malicious prompt injections."""
    # We only scan the first 1000 characters to keep it fast
    result = ingress_scanner(text[:1000], truncation=True, max_length=512)
    label = result[0]['label']
    score = result[0]['score']

    # If the model is highly confident it's an injection, block it
    if label == "INJECTION" and score > 0.8:
        logging.info(f"🚨 INGRESS FIREWALL TRIGGERED: {score} confidence.")
        return True
    return False


@rag_router.post("/") # Post request from the end-user
async def generate_summary(
    request: Request,
    file: UploadFile,
    run_eval: bool = Form(False), # <-- Added: Catches the checkbox state (defaults to False if unchecked)
    user_id:str = Depends(verify_token)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        pdf_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_file:
            temporary_file.write(pdf_bytes)
            pdf_path = temporary_file.name

        reader = PdfReader(pdf_path)
        first_page_text = reader.pages[0].extract_text() if len(reader.pages) > 0 else ""


        async def event_generator():
            try:
                yield f"data: {json.dumps({'type': 'status', 'step': 'Validating Medical Document...'})}\n\n"

                # Run the LLM/Heuristic validation
                is_valid = await validate_medical_document(first_page_text)

                if not is_valid:
                    # Send the exact error string back to the UI and safely terminate the stream
                    error_msg = "Invalid Document: CliniClarity only accepts medical records, lab results, or clinical reports."
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    return  # Exit the generator immediately; the LangGraph will NOT run

                yield f"data: {json.dumps({'type': 'status', 'step': 'Scanning for Cyber Threats...'})}\n\n"
                is_attack = await scan_for_prompt_injection(first_page_text)

                if is_attack:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Security Alert: Malicious prompt injection detected in document.'})}\n\n"
                    return  # Kills the stream BEFORE LangGraph ever runs!
                initial_state = {
                    "file_path": pdf_path,
                    "status": True,
                    "documents": [],
                    "context": [],
                    "summary": "",
                    "run_eval": run_eval,
                    "user_id": user_id
                }

                current_state = initial_state.copy()
                async for output in rag_app.astream(initial_state): # Stream the graph nodes by passing an initial state to the nodes
                    for node_name, state_update in output.items(): # Iterate through the state dictionary to extract node and state updates
                        yield f"data: {json.dumps({'type': 'status', 'step': node_name})}\n\n" # Yield the completed processing node name to frontend
                        current_state.update(state_update) # Update the dictionary instead of overwriting

                if current_state.get("status"): # Graph execution is done
                    draft_response = current_state["summary"]
                    doc_hash = current_state.get("doc_hash")
                    if doc_hash and not current_state.get('is_cached'):
                        storage_client = storage.Client()
                        bucket_name = os.environ.get("CACHE_BUCKET_NAME", "cliniclarity-doc-cache")
                        cache_blob = storage_client.bucket(bucket_name).blob(f"{user_id}/{doc_hash}.txt")
                        cache_blob.upload_from_string(draft_response)
                        logging.info(f"💾 Saved new summary to 15-minute cache: {doc_hash}.txt")
                    html_markdown = markdown.markdown(draft_response) # Extract the final generated summary from the state-graph

                    context = {
                        "request": request,
                        "summary_html": html_markdown,
                        "chunks": len(current_state.get("documents", [])),
                        "sources": 1,
                        "firebase_api_key": os.getenv("FIREBASE_API_KEY"),
                        "firebase_auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN"),
                        "firebase_project_id": "cliniclarity"
                    }

                    template_response = templates.TemplateResponse(
                        request=request,
                        name="report.html",
                        context=context
                    )

                    final_html = template_response.body.decode('utf-8')
                    yield f"data: {json.dumps({'type': 'complete', 'html': final_html})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Error in pipeline'})}\n\n"

            except Exception as e: yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            finally:
                if os.path.exists(pdf_path): os.remove(pdf_path)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

from Agent.RAG_Graph.Ingestion import vector_database


@rag_router.post("/logout-purge")
async def logout_purge(user_id: str = Depends(verify_token)):
    """
    Deletes all vectors associated with the user_id from Pinecone
    and wipes the specific document summary from Cloud Storage.
    """
    try:
        try:
            vector_database.delete(delete_all = True, namespace=user_id)
            logging.info(f"🧹 Pinecone vectors purged for user: {user_id}")
        except Exception as ex:
            logging.info(f"ℹ️ Pinecone namespace '{user_id}' likely already empty. ({ex})")


        bucket_name = os.environ.get("CACHE_BUCKET_NAME", "cliniclarity-doc-cache")
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=f"{user_id}/")
        deleted_count = 0

        for blob in blobs:
            blob.delete()
            deleted_count += 1

        return {"status": "success", "message": f"Zero-retention purge complete for {user_id}."}

    except Exception as e:
        logging.error(f"Purge Error: {e}")
        raise HTTPException(status_code=500, detail=f"Purge failed: {str(e)}")