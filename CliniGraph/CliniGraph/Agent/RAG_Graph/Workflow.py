from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END # Import the terminator node and the StateGraph class
from Agent.RAG_Graph.State import GraphState # Import the state-dictionary
from Agent.RAG_Graph.Ingestion import load_pdf, redact_PII, ingestion, SUMMARY_CACHE # Import functions from ingestion module
from Agent.RAG_Graph.Retrieval import summarize # Import function from retrieval module
from Agent.Security.Hallucination import hallucination # Import hallucination module
from Agent.Reflection.Graph import audit_app

workflow = StateGraph(state_schema=GraphState) # Create a LangGraph workflow

def format_cached_response(state:GraphState):
    """Wraps the retrieved summary in the friendly architect message"""
    cached_summary = state.get('summary')

    friendly_message = (
        "### ♻️ Document Already Processed\n\n"
        "**As the Lead Clinical Document Architect, I recognize this file.** "
        "It appears you have uploaded a document we have already summarized. "
        "To save processing time, I have instantly retrieved your previously generated report below. "
        "Please provide new medical documentation or a 'CORRECTIVE MEMO' if you need revisions.\n\n"
        "---\n\n"
        f"{cached_summary}"  # Append the actual previously generated summary here
    )

    return {"summary": friendly_message}

def route_after_load(state: GraphState):
    # If the document is recognized, skip the heavy AI processing
    if state.get("is_cached"):
        return "cached_response"
    # Otherwise, continue to your standard privacy pipeline
    return "redact"

def audit_loop(state:GraphState):
    print("\n" + "=" * 60)
    print("🔄 INITIATING REFLEXION AUDIT LOOP (Gemini Flash vs. Flash)")
    print("=" * 60)
    summary_text = str(state.get('summary', ''))
    initial_input = {"messages": [HumanMessage(content=summary_text)]}
    audit_result = audit_app.invoke(input=initial_input)
    final_llm_summary = audit_result['messages'][-2].content
    score = state.get('evaluation_score', 1.0)
    score_pct = int(score * 100)
    doc_hash = state.get("doc_hash")

    if doc_hash:
        SUMMARY_CACHE[doc_hash] = final_llm_summary

    trust_badge_html = f"""
<div class="mt-8 p-6 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl flex items-start gap-4 shadow-sm">
    <div class="text-emerald-500 text-3xl">🛡️</div>
    <div>
        <h4 class="text-emerald-900 dark:text-emerald-100 font-bold text-lg flex items-center gap-2 mb-1">
            Clinical Verification Score: {score_pct}% 
        </h4>
        <div class="flex flex-wrap gap-2 mb-3">
            <span class="bg-emerald-100 dark:bg-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-xs px-2.5 py-1 rounded-full uppercase tracking-wider font-bold">
                ✅ ACCEPTED (Grounded)
            </span>
            <span class="bg-blue-100 dark:bg-blue-800/60 text-blue-700 dark:text-blue-300 text-xs px-2.5 py-1 rounded-full uppercase tracking-wider font-bold">
                🔒 HIPAA COMPLIANT PIPELINE
            </span>
        </div>
        <p class="text-emerald-700 dark:text-emerald-400 text-sm leading-relaxed mb-0">
            This summary was audited by the DeepEval HIPAA-compliant security engine. The score confirms the AI adhered strictly to your anonymized records, ensuring privacy and clinical accuracy.
        </p>
    </div>
</div>
    """

    # Combine the final text and the HTML
    final_summary_with_badge = final_llm_summary + "\n\n" + trust_badge_html
    return {'summary': final_summary_with_badge}

def route_after_summarize(state: GraphState) -> str: # A router function to determine workflow execution
    if state.get("run_eval", True): # Retrieve property that indicates whether the user wants evaluation to be executed
        return "run_eval" # Execute the evaluation node
    else: # User wants to bypass the evaluation
        return "skip_eval" # Skip the evaluation and output generation

def route_evaluation(state:GraphState): # Another router function to determine workflow execution
    if state.get('evaluation_score', 0.0) > 0.9: # Retrieve property that holds the evaluation score
        return 'success' # Evaluation score meets a required threshold
    else: # Evaluation score does not meet a required threshold
        return 'failure' # Evaluation does not meet the required threshold

workflow.add_node('load', load_pdf) # Create a node representing the PDF loader into LangChain documents
workflow.add_node('redact', redact_PII) # Create a node representing redaction processes on the loaded documents
workflow.add_node('ingestion', ingestion) # Create a node representing an ingestion process into Pinecone Database
workflow.add_node('summarize', summarize) # Create a node representing a summary generation process
workflow.add_node('hallucination', hallucination) # Create a node representing the hallucination evaluator
workflow.add_node('audit', audit_loop)
workflow.add_node('format_cached', format_cached_response)

# workflow.add_edge('load', 'redact') # An edge connecting the load node to the redaction node (load -> redact)
workflow.add_edge('redact', 'ingestion') # An edge connecting the redaction node to the ingestion node (load -> redact -> ingestion)
workflow.add_edge('ingestion', 'summarize') # An edge connection the ingestion node to the summary generation node (load -> redact -> ingestion -> summarize)

workflow.add_conditional_edges('load', route_after_load, path_map={"cached_response": 'format_cached', 'redact': 'redact'})

workflow.add_conditional_edges('summarize', # Source node that needs to finish executing
                               route_after_summarize, # Router function executed once the source node finishes
                               path_map={"run_eval": 'hallucination', # The key matches with a string object returned by router
                                         "skip_eval": END}) # END is a terminator node to stop the graph's execution

workflow.add_conditional_edges('hallucination', # Hallucination node that outputs an evaluation score
                               route_evaluation, # Router function to evaluate the score
                               path_map={"success": 'audit', # Score meets the required threshold
                                         "failure": 'summarize'}) # Regenerate summary because there are hallucinations in the output



workflow.add_edge('audit', END)
workflow.add_edge('format_cached', END)

workflow.set_entry_point('load') # Entry point for the workflow

rag_app = workflow.compile() # Compile the workflow into a Runnable object
rag_app.get_graph().draw_mermaid_png(output_file_path="data.png") # Retrieve graph object into a mermaid diagram