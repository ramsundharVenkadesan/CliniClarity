from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from Agent import Queries
from RAG import verify_token
from fastapi import Depends

react_router = APIRouter(tags=["Queries"], prefix="/question")


@react_router.post("/")
async def ask_question(request: Request, user_id:str=Depends(verify_token)):
    data = await request.json()
    user_query = data.get("question")

    # Get the value, it might be an empty string if the template failed to render it
    llm_selection = data.get("llm_selection")

    # Robust fallback: check if it's falsy or missing the pipe delimiter
    if not llm_selection or "|" not in llm_selection:
        llm_selection = "google_genai|gemini-3-flash-preview"

    provider, model_name = llm_selection.split("|")

    # Call the standalone generator, no graph required
    return StreamingResponse(
        Queries.ask_question(user_query, model_name, provider, user_id),
        media_type="text/event-stream"
    )