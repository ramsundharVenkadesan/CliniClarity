from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from Agent.Reflection.Chains import generation, reflection
from Agent.Reflection.State import MessageGraph

load_dotenv()

def generation_node(state:MessageGraph):
    messages = state.get('messages', [])
    iteration = (len(messages) // 2) + 1

    if iteration == 1:
        print(f"\n👨‍⚕️ [ARCHITECT - Pass {iteration}]: Drafting initial clinical summary...")
    else:
        print(f"\n👨‍⚕️ [ARCHITECT - Pass {iteration}]: Reading Auditor's Memo and revising summary...")

    response = generation.invoke(input={'messages': state.get('messages')})

    if isinstance(response.content, list):
        if len(response.content) > 0 and isinstance(response.content[0], dict) and 'text' in response.content[0]:
            response.content = response.content[0]['text']
        else:
            response.content = str(response.content)
    return {"messages": [response]}

def reflection_node(state:MessageGraph):
    print("🕵️‍♂️ [AUDITOR]: Evaluating draft for jargon, structure, and hallucinations...")
    try:
        reflection_result = reflection.invoke(input={'messages': state.get('messages')})
        if reflection_result.is_approved:
            print("   ✅ VERDICT: PASSED. Summary meets all safety standards.")
            return {'messages': [HumanMessage(content="PASSED")]}
        else:
            print("   ❌ VERDICT: FAILED. Issuing Corrective Memo.")
            print(f"   📝 MEMO: {reflection_result.corrective_memo}")
            return {"messages": [HumanMessage(content=f"CORRECTIVE MEMO: {reflection_result.corrective_memo}")]}
    except Exception as e:
        print(f"   ⚠️ PARSING ERROR: Auditor failed to output valid JSON. Forcing retry. ({e})")
        # Catch JSON parsing errors and force the LLM to try again
        print(f"--- PARSING ERROR: {e} ---")
        return {
            "messages": [HumanMessage(content="CORRECTIVE MEMO: You failed to output valid JSON. Please try again.")]}

def should_audit(state:MessageGraph):
    message = state.get('messages')
    last_message = message[-1]

    if len(message) > 6:
        print("\n🛑 ROUTER: Maximum retries reached (3 loops). Forcing exit.")
        return END
    elif "PASSED" in last_message.content:
        print("\n🏁 ROUTER: Audit complete. Finalizing report for UI.")
        return END
    else:
        print("\n⏪ ROUTER: Sending memo back to Architect for immediate revision.")
        return 'generation'



message_graph = StateGraph(state_schema=MessageGraph)

message_graph.add_node('generation', generation_node)
message_graph.add_node('reflection', reflection_node)

message_graph.set_entry_point('generation')
message_graph.add_edge('generation', 'reflection')

message_graph.add_conditional_edges('reflection', should_audit, path_map={END:END, 'generation': 'generation'})

audit_app = message_graph.compile()