from langgraph.graph import StateGraph, END
from Agent.RAG_Graph.State import GraphState
from Agent.RAG_Graph.Ingestion import load_pdf, redact_PII, ingestion
from Agent.RAG_Graph.Retrieval import summarize

workflow = StateGraph(state_schema=GraphState)

workflow.add_node('load', load_pdf)
workflow.add_node('redact', redact_PII)
workflow.add_node('ingestion', ingestion)
workflow.add_node('summarize', summarize)

workflow.add_edge('load', 'redact')
workflow.add_edge('redact', 'ingestion')

workflow.add_edge('ingestion', 'summarize')
workflow.add_edge('summarize', END)

workflow.set_entry_point('load') # Tells the graph where to start
rag_app = workflow.compile()
rag_app.get_graph().draw_mermaid_png(output_file_path="data.png")