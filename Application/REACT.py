from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from Agent import Queries

react_router = APIRouter(tags=["Queries"], prefix="/question")


@react_router.post("/")
async def ask_question(request: Request):
    data = await request.json()
    user_query = data.get("question")

    llm_selection = data.get("llm_selection", "google_genai|gemini-3-flash-preview")
    provider, model_name = llm_selection.split("|")

    # Call the standalone generator, no graph required
    return StreamingResponse(
        Queries.ask_question(user_query, model_name, provider),
        media_type="text/event-stream"
    )