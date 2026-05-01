from typing import TypedDict, List # Import Type-Hints package
from langchain_core.documents import Document # Import the Document class from LangChain

class GraphState(TypedDict): # Typed-Dictionary class to maintain and hold state between nodes in the graph
    summary:str # Property to maintain
    file_path:str # URL to the original input file
    documents: List[Document] # A property used during the ingestion pipeline to load, redact, and vectorize the input PDF
    status:bool # A property to ensure each ingestion node's execution was successful (Any errors will set the property to False)
    context:List[str] # Relevant-Chunks retrieved from a vector database to generate a summary
    evaluation_score:float # A floating-point score assigned to the generated summary based on the input PDF
    run_eval:bool # Toggle to execute Deep-Eval on summary generation (increases execution time)
    is_cached: bool # Property to maintain caching
    pdf_text:str # Property to extract PDF text data
    doc_hash:str # Property to store unique document hash
    user_id:str # Property to store user-ID