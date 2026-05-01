from dotenv import load_dotenv # Import function to retrieve environment variables
from langchain_core.messages import HumanMessage # Import Human-Message class
from langgraph.graph import END, StateGraph # Import State-Graph and Terminator node
from Agent.Reflection.Chains import generation, reflection # Import generation and reflection runnable chains
from Agent.Reflection.State import MessageGraph # Import state dictionary
from typing import Dict, Any # Import Typing package
import logging # Import the logging package

load_dotenv() # Invoke function to load API keys

def generation_node(state:MessageGraph) -> Dict[str, Any]: # Node function to generate a summary
    messages = state.get('messages', []) # Retrieve messages in the state dictionary
    iteration = (len(messages) // 2) + 1 # Number of iterations required

    if iteration == 1: # Number of current iteration is one
        logging.info(f"\n️ [ARCHITECT - Pass {iteration}]: Drafting initial clinical summary...") # Draft the initial summary
    else: # The iteration is above one
        logging.info(f"\n [ARCHITECT - Pass {iteration}]: Reading Auditor's Memo and revising summary...") # Read the corrective memo and revise the summary

    response = generation.invoke(input={'messages': state.get('messages')}) # Invoke the generation node by retrieving messages from state dictionary

    if isinstance(response.content, list): # The response generated in a list object
        if (len(response.content) > 0) and (isinstance(response.content[0], dict)) and 'text' in (response.content[0]): # Response is a dictionary with text field
            response.content = response.content[0]['text'] # Retrieve the first element from list object and text key
        else: # The response is not a dictionary
            response.content = str(response.content) # Retrieve content and convert it to a string object
    return {"messages": [response]} # Update state dictionary with response

def reflection_node(state:MessageGraph) -> Dict[str, Any]: # Node function to reflect on the generated summary
    logging.info("🕵️‍♂️ [AUDITOR]: Evaluating draft for jargon, structure, and hallucinations...")

    try: # Code block to contain erroneous code
        reflection_result = reflection.invoke(input={'messages': state.get('messages')}) # Invoke the reflection node by extracting messages from state-dictionary

        if reflection_result.is_approved: # The node approves the result
            logging.info("VERDICT: PASSED. Summary meets all safety standards.")
            return {'messages': [HumanMessage(content="PASSED")]} # Update state-dictionary with summary PASSED
        else: # The node does not approve the result
            logging.info("VERDICT: FAILED. Issuing Corrective Memo.") # The summary failed the checks
            logging.info(f"MEMO: {reflection_result.corrective_memo}") # The corrective memo is returned by the LLM
            return {"messages": [HumanMessage(content=f"CORRECTIVE MEMO: {reflection_result.corrective_memo}")]} # Update state dictionary with corrective memo required to fix the summary
    except Exception as e: # Exception block catch exceptions (Catch JSON parsing errors and force the LLM to try again)
        logging.info(str(e))
        return {"messages": [HumanMessage(content="CORRECTIVE MEMO: You failed to output valid JSON. Please try again.")]} # Update state dictionary with the error message

def should_audit(state:MessageGraph) -> str: # Router function to determine routes between nodes
    message = state.get('messages') # Retrieve the messages from state dictionary
    last_message = message[-1] # Retrieve the last message from the dictionary

    if len(message) > 8: # Length of messages list is greater than 8
        logging.info("ROUTER: Maximum retries reached (3 loops). Forcing exit.") # Write the error details to logging file
        return END # Return the terminator node
    elif "PASSED" in last_message.content: # Check if the summary passes the checks
        return END # Return the terminator node
    else: # None of the above conditions matched
        logging.info("\nROUTER: Sending memo back to Architect for immediate revision.") # Router is sending memo back to architect
        return 'generation' # Return a string object representing generation node



message_graph = StateGraph(state_schema=MessageGraph) # Compile the workflow into a graph by passing the schema

message_graph.add_node('generation', generation_node) # Create a node representing summary generation
message_graph.add_node('reflection', reflection_node) # Create a node representing summary reflection

message_graph.set_entry_point('generation') # Set the generation node as entry point
message_graph.add_edge('generation', 'reflection') # An edge connection generation and reflection nodes

message_graph.add_conditional_edges('reflection', # The reflection must finish executing
                                    should_audit, # The router function to determine route
                                    path_map={END:END, # Terminate execution
                                              'generation': 'generation'}) # Generate content

audit_app = message_graph.compile() # Compile the graph to be executed