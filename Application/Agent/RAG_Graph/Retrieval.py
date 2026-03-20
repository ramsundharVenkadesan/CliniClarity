from langchain.chat_models import init_chat_model
from typing import Dict, Any
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from Agent.RAG_Graph.State import GraphState
from Agent.RAG_Graph.Ingestion import vector_database
from Agent.Prompts import Retrieval_Prompt


def format_documents(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def summarize(state:GraphState) -> Dict[str, Any]:
    if state['status']:
        dynamic_model = init_chat_model(model="gemini-3-flash-preview", temperature=0.0, model_provider="google_genai")

        system_prompt = """
        You are a compassionate Patient Advocate, Health Literacy Expert, and a Clinical Data Auditor enforcing strict HIPAA 'Minimum Necessary' standards.
        Summarize the provided clinical context into a highly readable report for a patient.
        Your goal is to explain a complex medical report to someone with NO medical background. 

        Strict Compliance Rules:
        1. Principle of Least Privilege: Do NOT extract or pass along any incidental medical history, diagnoses, or notes that do not directly relate to the patient's specific question.
        2. Zero Hallucination: You are strictly limited to the provided text. If the text does not contain the answer, output exactly: "NO_CLINICAL_EVIDENCE_FOUND". Do not infer or provide outside medical knowledge.
        3. Maintain Anonymity: Do not output any names, dates, or facility locations if they accidentally bypassed the redaction pipeline."""

        prompt_template = ChatPromptTemplate.from_template(template=Retrieval_Prompt.medical_summary_template).partial(system_prompt=system_prompt)
        retriever = vector_database.as_retriever(search_kwargs={"k": 5})
        retrieved_docs = retriever.invoke(input="Summarize the report")
        context_list = [doc.page_content for doc in retrieved_docs]
        context_text = format_documents(retrieved_docs)

        chain = prompt_template | dynamic_model | StrOutputParser()


        response = await chain.ainvoke(input={"query": "Summarize the report", "context": context_text})
        return {"summary": response, "context":context_list}
    else:
        raise Exception("Error: Something went wrong in the ingestion step!")
