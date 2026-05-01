import markdown, tempfile, json, os # Import helper classes
from fastapi import APIRouter, UploadFile, HTTPException, Request, Form, Depends # Import classes from FastAPI package
from fastapi.responses import StreamingResponse # Import class to stream response
from starlette.templating import Jinja2Templates # Import class to render HTML files
from Agent.RAG_Graph.Workflow import rag_app # Import the complied graph
from pypdf import PdfReader # Import class to read input PDF documents
from Agent.Security.Validation import * # Import validation functions
from google.cloud import storage # Import GCS storage client
from firebase_admin import auth # Import Firebase Admin authentication
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Import Bearer token and Authorization Credentials class
from Agent.RAG_Graph.Ingestion import vector_database # Import the Pinecone Vector-Database
from Agent.Security.PromptInjection import is_prompt_injection

storage_client = storage.Client() # Initialize GCS storage client
import logging # Import logging framework

security = HTTPBearer() # A gatekeeper to check incoming requests for a valid identity credential before allowing the code to execute

def verify_token(credentials:HTTPAuthorizationCredentials=Depends(security)): # Function to verify the Firebase JWT
    """Middleware to verify the user's Firebase JWT.""" # Doc-String used as metadata
    try: # Try code-block
        decoded_token = auth.verify_id_token(credentials.credentials) # Verify token with Firebase
        return decoded_token.get('uid') # Retrieve and return user-ID
    except Exception as e: # Catch any errors thrown by the try-block
        logging.error(f"🚨 FIREBASE AUTH ERROR: {str(e)}") # Log the Authentication Error
        raise HTTPException(status_code=401, detail="Invalid or expired token.") # Raise a 401 Unauthorized Exception

rag_router = APIRouter(tags=["Summary"], prefix="/summary") # API Router to generate a summary
templates = Jinja2Templates(directory="templates") # Retrieve HTML files from the templates directory


@rag_router.post("/") # Post Request to accept input document(s) from user
async def generate_summary(request: Request, file: UploadFile, run_eval: bool = Form(False), user_id:str = Depends(verify_token)): # Asynchronous function to generate a summary from input documents
    if not file.filename.endswith(".pdf"): raise HTTPException(status_code=400, detail="Invalid file type.") # Input document is not a valid PDF

    try: # Try code-block
        pdf_bytes = await file.read() # Read all the bytes from the input PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_file: # Create a temporary PDF file
            temporary_file.write(pdf_bytes) # Write the bytes from input PDF file to temporary file
            pdf_path = temporary_file.name # Extract absolute path of the temporary file

        reader = PdfReader(pdf_path) # Read the PDF file
        first_page_text = reader.pages[0].extract_text() if len(reader.pages) > 0 else "" # Retrieve text from first page of the PDF document


        async def event_generator(): # Inner asynchronous function to invoke the RAG Agent
            try: # Try code-block
                yield f"data: {json.dumps({'type': 'status', 'step': 'Validating Medical Document...'})}\n\n" # Validation Step

                is_valid = await validate_medical_document(first_page_text) # Invoke function to validate medical document's content

                if not is_valid: # The input document is not a valid medical document
                    error_msg = "Invalid Document: CliniClarity only accepts medical records, lab results, or clinical reports." # Send the exact error string back to the UI and safely terminate the stream
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n" # Error message to terminate stream
                    return # Exit the generator immediately

                yield f"data: {json.dumps({'type': 'status', 'step': 'Scanning for Cyber Threats...'})}\n\n" # Scanning medical document

                is_attack = await is_prompt_injection(first_page_text[:1000]) # Invoke function to scan for any prompt injection

                if is_attack: # The input document contains malicious content
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Security Alert: Malicious prompt injection detected in document.'})}\n\n" # Error message to terminate stream
                    return # Exit the generator immediately

                initial_state = {"file_path": pdf_path, "status": True, "documents": [], "context": [], "summary": "", "run_eval": run_eval, "user_id": user_id} # Dictionary to initialize state-graph
                current_state = initial_state.copy() # Copy the initial state dictionary

                async for output in rag_app.astream(initial_state): # Stream the graph nodes by passing an initial state to the nodes
                    for node_name, state_update in output.items(): # Iterate through the state dictionary to extract node and state updates
                        yield f"data: {json.dumps({'type': 'status', 'step': node_name})}\n\n" # Yield the completed processing node name to frontend
                        current_state.update(state_update) # Update the dictionary instead of overwriting

                if current_state.get("status"): # Retrieve current state-graph status
                    draft_response = current_state["summary"] # Retrieve the summary from state-graph
                    doc_hash = current_state.get("doc_hash") # Retrieve the document hash from state-graph

                    if doc_hash and not current_state.get('is_cached'): # The document is not cached
                        storage_client = storage.Client() # Connect the GCS bucket
                        bucket_name = os.environ.get("CACHE_BUCKET_NAME", "cliniclarity-doc-cache") # Retrieve the cache bucket
                        cache_blob = storage_client.bucket(bucket_name).blob(f"{user_id}/{doc_hash}.txt") # Create a new object in the cache bucket
                        cache_blob.upload_from_string(draft_response) # Upload the summary to the cache bucket
                        logging.info(f"💾 Saved new summary to 15-minute cache: {doc_hash}.txt") # Log the cache-write
                    html_markdown = markdown.markdown(draft_response) # Extract the final generated summary from the state-graph

                    context = {"request": request, "summary_html": html_markdown, # Construct a dictionary with required data
                        "chunks": len(current_state.get("documents", [])), "sources": 1, # Retrieve number of chunks in the state dictionary and sources
                        "firebase_api_key": os.getenv("FIREBASE_API_KEY"), "firebase_auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN"), "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID") } # Firebase authentication keys

                    template_response = templates.TemplateResponse(request=request, name="report.html", context=context) # Create a Template-Response with context

                    final_html = template_response.body.decode('utf-8') # Decode the template response instance
                    yield f"data: {json.dumps({'type': 'complete', 'html': final_html})}\n\n" # Dump the final HTML file

                else: yield f"data: {json.dumps({'type': 'error', 'message': 'Error in pipeline'})}\n\n" # Error executing the pipeline

            except Exception as e: yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n" # Raise an exception

            finally: # Finally block
                if os.path.exists(pdf_path): os.remove(pdf_path) # Remove the input PDF file

        return StreamingResponse(event_generator(), media_type="text/event-stream") # Stream the response back to UI

    except Exception as e: raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}") # Catch any file-processing exceptions


@rag_router.post("/logout-purge") # Post Request to log-out
async def logout_purge(user_id: str = Depends(verify_token)): # Asynchronous function to allow users to sign-out
    """
    Deletes all vectors associated with the user_id from Pinecone
    and wipes the specific document summary from Cloud Storage.
    """ # Doc-String used as metadata

    try: # Try code-block
        try: # Inner try code-block
            vector_database.delete(delete_all = True, namespace=user_id) # Delete all vectors associated with the user_id
            logging.info(f"🧹 Pinecone vectors purged for user: {user_id}") # Log the purge
        except Exception as ex: logging.info(f"ℹ️ Pinecone namespace '{user_id}' likely already empty. ({ex})") # Raise an exception to indicate the namespace is empty

        bucket_name = os.environ.get("CACHE_BUCKET_NAME", "cliniclarity-doc-cache") # Retrieve the cache-bucket
        bucket = storage_client.bucket(bucket_name) # Access the cache-bucket
        blobs = bucket.list_blobs(prefix=f"{user_id}/") # Retrieve all objects in the user's namespace
        deleted_count = 0 # Variable to keep track of number of objects deleted

        for blob in blobs: # Iterate through objects in the user's namespace
            blob.delete() # Delete each object from bucket
            deleted_count += 1 # Increment the delete-count

        return {"status": "success", "message": f"Zero-retention purge complete for {user_id}."} # Return success message

    except Exception as e: # Raise an exception
        logging.error(f"Purge Error: {e}") # Error emptying the bucket
        raise HTTPException(status_code=500, detail=f"Purge failed: {str(e)}") # Raise exception to indicate the purge failed