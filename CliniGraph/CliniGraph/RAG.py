import markdown, tempfile, json
from fastapi import APIRouter, UploadFile, HTTPException, Request, Form
from fastapi.responses import StreamingResponse
from starlette.templating import Jinja2Templates
from Agent.RAG_Graph.Workflow import rag_app # Import the complied graph

rag_router = APIRouter(tags=["Summary"], prefix="/summary")
templates = Jinja2Templates(directory="templates")


@rag_router.post("/") # Post request from the end-user
async def generate_summary(
    request: Request,
    file: UploadFile,
    run_eval: bool = Form(False) # <-- Added: Catches the checkbox state (defaults to False if unchecked)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        pdf_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_file:
            temporary_file.write(pdf_bytes)
            pdf_path = temporary_file.name

        initial_state = {"file_path": pdf_path, "status": True, "documents": [], # Dictionary object representing the state graph
            "context": [], # Each key represents a field in the state graph
            "summary": "", "run_eval": run_eval # Toggle to run the evaluation
        } # Initial state injected into the state-dictionary

        current_state = initial_state.copy() # Define a dictionary to keep a running track of the state

        async def event_generator():
            try:
                async for output in rag_app.astream(initial_state): # Stream the graph nodes by passing an initial state to the nodes
                    for node_name, state_update in output.items(): # Iterate through the state dictionary to extract node and state updates
                        yield f"data: {json.dumps({'type': 'status', 'step': node_name})}\n\n" # Yield the completed processing node name to frontend
                        current_state.update(state_update) # Update the dictionary instead of overwriting

                if current_state.get("status"): # Graph execution is done
                    html_markdown = markdown.markdown(current_state["summary"]) # Extract the final generated summary from the state-graph

                    template_response = templates.TemplateResponse("report.html", {
                        "request": request,
                        "summary_html": html_markdown,
                        "chunks": len(current_state.get("documents", [])),
                        "sources": 1
                    }) # Response sent to the front-end

                    final_html = template_response.body.decode('utf-8')
                    yield f"data: {json.dumps({'type': 'complete', 'html': final_html})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Error in pipeline'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        # 3. Return the stream
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))