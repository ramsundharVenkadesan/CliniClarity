from typing import TypedDict, List
from langchain_core.documents import Document

class GraphState(TypedDict):
    summary:str
    file_path:str
    documents: List[Document]
    status:bool
    context:List[str]
    evaluation_score:float