from fastapi import APIRouter, Request # Import API Router class and Request class
from fastapi.responses import StreamingResponse # Import Streaming-Response Class
from Agent import Queries # Import module with ReACT agent
from RAG import verify_token # Import function to verify JWT token
from fastapi import Depends # Import Dependency injection class

react_router = APIRouter(tags=["Queries"], prefix="/question") # API Router to answer user questions


@react_router.post("/") # Post Request to allow users to ask questions
async def ask_question(request: Request, user_id:str=Depends(verify_token)): # Asynchronous function to allow user to ask question(s)
    data = await request.json() # Retrieve the request passed by user
    user_query = data.get("question") # Retrieve the question from the request JSON

    llm_selection = data.get("llm_selection") # Retrieve LLM selection

    if not llm_selection or "|" not in llm_selection: llm_selection = "google_genai|gemini-3-flash-preview" # Choose the Gemini model

    provider, model_name = llm_selection.split("|") # Split the string into provider and model

    return StreamingResponse( # Call the generator function
        Queries.ask_question(user_query, model_name, provider, user_id), # Invoke AI agent that accepts user questions
        media_type="text/event-stream") # Stream response back to user