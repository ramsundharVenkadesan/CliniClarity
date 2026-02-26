from langchain.chat_models import init_chat_model
from typing import Dict, Any
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

from Agent.Ingestion import vector_database

gemini_model = init_chat_model(model="gemini-3-flash-preview", model_provider="google_genai", temperature=0.0)

medical_summary_template = """
            SYSTEM: You are a compassionate Patient Advocate and Health Literacy Expert. 
            Your goal is to explain a complex medical report to someone with NO medical background. 

            CLINICAL CONTEXT: 
            {context}

            USER QUERY: 
            {query}

            INSTRUCTIONS for Accessibility:
            - Use a 6th-grade reading level. 
            - Avoid medical jargon. If you must use a term (e.g., 'Spiculated'), explain it simply (e.g., 'spiky or irregular shape').
            - Use the 'What, So What, Now What' framework.
            - Use emojis to make the report less intimidating.

            # 🩺 Your Health Summary (Simplified)
            ---
            ## 💡 The Main Takeaway (The 'What')
            [Provide a 2-sentence summary using everyday language. Example: 'The doctors found a spot on your lung that needs more testing right away.']

            ## 🔍 What the Results Mean (The 'So What')
            - **The Finding:** [Explain the primary issue without using scary jargon unless defined.]
            - **Why it matters:** [Explain why the doctor is concerned in a calm, supportive way.]

            ## 📊 Key Labs & Vitals
            [Only list the most important ones. Explain 'High' or 'Low' instead of just numbers.]
            - **Blood Sugar:** [Explain it like: 'Higher than normal, which means your diabetes needs more attention.']

            ## 🚶 Your Next Steps (The 'Now What')
            1. **Priority 1:** [Most urgent action]
            2. **Priority 2:** [Next follow-up]

            ## ❓ Questions for your Doctor
            [Provide 2 questions the patient can literally read out loud to their doctor at the next visit.]

            ---
            *Disclaimer: This is an AI-generated summary to help you understand your report. Please discuss all findings with your healthcare team.*
"""

def format_documents(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def summarize() -> Dict[str, Any]:
    prompt_template = ChatPromptTemplate.from_template(template=medical_summary_template)
    retriever = vector_database.as_retriever(search_kwargs={"k": 5})

    chain = (RunnablePassthrough.assign(context=itemgetter("query") | retriever | format_documents)
             | prompt_template | gemini_model | StrOutputParser())

    response = await chain.ainvoke(input={"query": "Summarize the report"})
    return response