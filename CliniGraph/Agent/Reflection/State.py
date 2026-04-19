from typing import TypedDict, Annotated # Import Type-Hints package
from langgraph.graph import add_messages # Import function to properly append messages to the state dictionary
from pydantic import BaseModel, Field


class MessageGraph(TypedDict): # State dictionary to maintain state between nodes
    messages:Annotated[list, add_messages] # A list of messages that will be maintained

class AuditEvaluator(BaseModel): # Custom schema class to properly audit the response
    is_approved:bool = Field(description="True if the summary has no jargon and no hallucinations.") # Field that ensures the final summary has no medical jargon
    corrective_memo:str = Field(description="If is_approved is False, list the exact bullet points to fix. If True, output 'PASSED'.") # Field to produce corrections when the summary is not passed