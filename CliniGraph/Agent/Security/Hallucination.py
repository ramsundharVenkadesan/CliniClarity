import asyncio, datetime, os, time # Import required Python packages
from typing import Dict, Any # Import Type-Hints package
from deepeval.test_case import LLMTestCase # Import Test-Case class
from deepeval.metrics import FaithfulnessMetric # Import Faithfulness Metric
from deepeval.models import DeepEvalBaseLLM # Import base LLM class
from langchain_google_genai import ChatGoogleGenerativeAI # Import Google Generative AI
from Agent.RAG_Graph.State import GraphState # Import state-dictionary

ACTIVITY_LOG_FILE = "/Users/ram/Downloads/CliniGraph/activity.log" # Log file to store evalution


class GeminiEvaluator(DeepEvalBaseLLM): # This safely bridges Gemini's API with DeepEval's internal parser
    def __init__(self, model_name="gemini-3.1-flash-lite-preview"): # Evaluator Model passed to constructor
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=0.0, google_api_key=os.environ.get("GOOGLE_API_KEY")) # Initialize an instance to connect to Gemini model

    def load_model(self): return self.model # Load the model

    def generate(self, prompt: str, **kwargs) -> str: # Method that accepts the evaluator prompt and dictionary of arguments
        chat_model = self.load_model() # Load the chat model

        if isinstance(prompt, list): # Check if the prompt is a list object
            try: # Attempt to evaluate prompt
                prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in prompt]) # Retrieve role and content from each prompt in the list object
            except Exception as e: # Prompt is not a list object
                prompt = str(prompt) # Convert prompt into a string object

        response = chat_model.ainvoke(prompt) # Invoke the LLM model
        content = response.content # Retrieve response from the evaluator model

        if isinstance(content, list): # Check if the response is a list object
            content = "".join([block.get("text", "") for block in content if isinstance(block, dict)]) # Convert the response list object into a string object
        return str(content) # Return the generated response

    async def a_generate(self, prompt: str, **kwargs) -> str: # Asynchronous version of the generate method
        chat_model = self.load_model() # Load the chat model

        if isinstance(prompt, list): # Check if the prompt is a list object
            try: # Attempt to evaluate prompt
                prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in prompt]) # Retrieve role and content from each prompt in the list object
            except Exception: # Prompt is not a list object
                prompt = str(prompt) # Convert prompt into a string object

        response = await chat_model.ainvoke(prompt) # Invoke the LLM model
        content = response.content # Retrieve response from the evaluator model

        if isinstance(content, list): # Check if the response is a list object
            content = "".join([block.get("text", "") for block in content if isinstance(block, dict)]) # Convert the response list object into a string object
        return str(content) # Return the generated response

    def get_model_name(self): return "Gemini Flash Lite" # Identify which model performed the audit logs



async def hallucination(state: GraphState) -> Dict[str, Any]: # Function to perform the checks
    print("\n--- 🛡️ RUNNING DEEPEVAL FAITHFULNESS CHECK ---") # Display to console

    summary, context, query = state.get('summary'), state['context'], "summarize the report" # Retrieve contents from state-dictionary

    gemini_judge = GeminiEvaluator() # Instantiate the safe Gemini wrapper

    metric = FaithfulnessMetric(threshold=0.9, model=gemini_judge, include_reason=False) # Initialize the HIPAA-ready DeepEval metric

    test_case = LLMTestCase(input=query, actual_output=summary, retrieval_context=context) # Initialize the test case for a model

    print("Evaluating Groundedness using DeepEval...")

    start_time = time.time() # Current time before evaluation

    try: # Attempt to perform evaluation
        if hasattr(metric, 'a_measure'): # Check if the metric supports native async measuring.
            await metric.a_measure(test_case) # Await the asynchronous measure function
            execution_time = time.time() - start_time # Total execution time of the evaluation

            # Audit logging for developer observability.
            print(f"[*] Evaluator Model : {gemini_judge.get_model_name()}")
            print(f"[*] Context Size    : {len(state['context'])} documents")
            print(f"[*] Summary Size    : {len(state['summary'])} characters")
            print(f"[*] Execution Time  : {execution_time:.2f} seconds")
            print(f"[*] Final Score     : {metric.score}")
            print(f"[*] Threshold Met   : {metric.is_successful()}")

        else: # Safely offload the synchronous measure function to a background thread
            await asyncio.to_thread(metric.measure, test_case) # This prevents the float return value from breaking the await expression
            execution_time = time.time() - start_time # Total execution time of the evaluation

            # Audit logging for developer observability.
            print(f"[*] Evaluator Model : {gemini_judge.get_model_name()}")
            print(f"[*] Context Size    : {len(state['context'])} documents")
            print(f"[*] Summary Size    : {len(state['summary'])} characters")
            print(f"[*] Execution Time  : {execution_time:.2f} seconds")
            print(f"[*] Final Score     : {metric.score}")
            print(f"[*] Threshold Met   : {metric.is_successful()}")

        score = metric.score # The score is stored in the metric object after execution

    except Exception as e: # Error in evaluation
        with open(ACTIVITY_LOG_FILE, mode="a") as file: # Open the log file to track errors
            file.write(f"[{datetime.datetime.now()}] DeepEval Execution Error: {e}\n") # Write the error to file
        score = 0.0 # Score set to 0

    print(f"DeepEval Score: {score}") # Final score to console

    if score > 0.9: # Score is above 90%
        print("Decision: ✅ ACCEPTED (Grounded in context)")
    else: # The score is below 90%
        print("Decision: ❌ REJECTED (Hallucination Detected)") # Hallucination detected # Assign the hallucinated summary

    return {"evaluation_score": score} # Update state-dictionary with the evaluation score and final summary
