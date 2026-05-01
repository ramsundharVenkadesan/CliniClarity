from langchain.chat_models import init_chat_model # Import function to initialize any chat model from any vendor
from typing import Dict, Any # Import Type-Hints package
from langchain_core.output_parsers import StrOutputParser # Import output-parser class to parse model output
from langchain_core.prompts import ChatPromptTemplate # Import class to create a prompt template passed to LLM
from Agent.RAG_Graph.State import GraphState # Import the state-dictionary
from Agent.RAG_Graph.Ingestion import vector_database # Import the vector database
from Agent.Prompts.Retrieval_Prompt import * # Import prompt string passed to the model
from Agent.Logging.CallBack import CallBackHandler # Import class to track LLM changes

callback_handler = CallBackHandler() # Handler to track LLM changes

def format_documents(docs) -> str: # Generic function to format retrieved documents
    return "\n\n".join(doc.page_content for doc in docs) # Retrieve each document's content and join them into a single string

async def summarize(state:GraphState) -> Dict[str, Any]: # Node to summarize the retrieved documents
    if state.get('status'): # Retrieve the ingestion status from the state dictionary
        user_id = state.get('user_id') # Retrieve user-ID associate with user
        dynamic_model = init_chat_model(model="gemini-3-flash-preview", temperature=0.0, model_provider="google_genai") # Create and initialize a LLM model

        system_prompt = """
        You are a compassionate Patient Advocate, Health Literacy Expert, and a Clinical Data Auditor enforcing strict HIPAA 'Minimum Necessary' standards.
        Summarize the provided clinical context into a highly readable report for a patient.
        Your goal is to explain a complex medical report to someone with NO medical background. 

        Strict Compliance Rules:
        1. Principle of Least Privilege: Do NOT extract or pass along any incidental medical history, diagnoses, or notes that do not directly relate to the patient's specific question.
        2. Zero Hallucination: You are strictly limited to the provided text. If the text does not contain the answer, output exactly: "NO_CLINICAL_EVIDENCE_FOUND". Do not infer or provide outside medical knowledge.
        3. Maintain Anonymity: Do not output any names, dates, or facility locations if they accidentally bypassed the redaction pipeline.""" # Developer instructions to ensure the model stays on course

        prompt_template = ChatPromptTemplate.from_template(template=medical_summary_template).partial(system_prompt=system_prompt) # Load the prompt string with developer instructions
        retriever = vector_database.as_retriever(search_kwargs={"k": 5, "namespace": user_id}) # Retriever object configured to retrieve 5 most relevant documents based on an input query
        retrieved_docs = retriever.invoke(input="Summarize the report") # Invoke the retriever object with an input query

        context_list = [doc.page_content for doc in retrieved_docs] # Iterate through a list of retrieved documents and extract their content
        context_text = format_documents(retrieved_docs) # Format the retrieved documents into a single string object

        chain = prompt_template | dynamic_model | StrOutputParser() # Runnable chain: Prompt -> Model -> Response -> Format-Response


        response = await chain.ainvoke(input={"query": "Summarize the report", "context": context_text}, # Invoke the chain by filling in input variables in the RAG prompt string
                                       config={"callbacks": [callback_handler]}) # Configure a call-back handler to ensure LLM changes are tracked

        return {"summary": response, "context": context_list} # Update the state dictionary with model's response and the retrieve context documents from database

    else: raise Exception("Error: Something went wrong in the ingestion step!") # Ingestion was not done correctly!
