from starlette import status
import markdown, tempfile, json
from fastapi import APIRouter, UploadFile, HTTPException, Request, Form
from fastapi.responses import StreamingResponse
from starlette.templating import Jinja2Templates

# IMPORT YOUR COMPILED GRAPH
from Agent.RAG_Graph.Workflow import rag_app

rag_router = APIRouter(tags=["Summary"], prefix="/summary")
templates = Jinja2Templates(directory="templates")


@rag_router.post("/")
async def generate_summary(
    request: Request,
    file: UploadFile,
    llm_selection: str = Form(...),
    run_eval: bool = Form(False) # <-- Added: Catches the checkbox state (defaults to False if unchecked)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        pdf_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temporary_file:
            temporary_file.write(pdf_bytes)
            pdf_path = temporary_file.name

        initial_state = {
            "file_path": pdf_path,
            "status": True,
            "documents": [],
            "context": [],
            "question": "Summarize the patient's medical report based on the provided documents.",
            "summary": "",
            "run_eval": run_eval # <-- Added: Injects the toggle state into LangGraph
        }

        # Define a dictionary to keep a running track of the state
        current_state = initial_state.copy()

        async def event_generator():
            try:
                # 1. Stream the graph nodes in real-time
                async for output in rag_app.astream(initial_state):
                    for node_name, state_update in output.items():
                        # Yield the completed node name to the frontend
                        yield f"data: {json.dumps({'type': 'status', 'step': node_name})}\n\n"

                        # Fix: Update the dictionary instead of overwriting it
                        current_state.update(state_update)

                # 2. Graph is finished, use the accumulated current_state
                if current_state.get("status"):
                    html_markdown = markdown.markdown(current_state["summary"])

                    template_response = templates.TemplateResponse("report.html", {
                        "request": request,
                        "summary_html": html_markdown,
                        "chunks": len(current_state.get("documents", [])),
                        "sources": 1,
                        "llm_selection": llm_selection
                    })

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