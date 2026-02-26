from fastapi import Request, APIRouter
from Agent import Queries

react_router = APIRouter(tags=["Queries"], prefix="/question")

@react_router.post("/")
async def ask_question(request:Request):
    data = await request.json()
    user_query = data.get("question")
    answer = await Queries.ask_question(user_query)
    return {"answer": answer}
