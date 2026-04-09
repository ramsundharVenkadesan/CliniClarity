from typing import TypedDict, Annotated # Import Type-Hints package
from langgraph.graph import add_messages # Import function to properly append messages to the state dictionary


class MessageGraph(TypedDict): # State dictionary to maintain state between nodes
    messages:Annotated[list, add_messages] # A list of messages that will be maintained