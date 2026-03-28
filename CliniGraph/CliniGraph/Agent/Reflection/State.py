from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class MessageGraph(TypedDict):
    messages:Annotated[list, add_messages]