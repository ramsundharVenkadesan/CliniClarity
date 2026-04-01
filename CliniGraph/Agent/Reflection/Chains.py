from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model # Import function to initialize a chat model
from pydantic import BaseModel, Field

load_dotenv()

reflection_sys_prompt = """You are a Senior Medical QA Auditor for CliniClarity. You are the final gatekeeper for patient safety and clarity.

Your Task:
Critique the Architect's generated summary provided in the message history. You are looking for:
1. Hallucinations: Are there any medical claims not supported by the source data?
2. Jargon: Are there complex terms (e.g., 'idiopathic', 'infarction') that haven't been simplified to a 6th-grade reading level?
3. Structure: Does it strictly follow the "What, So What, Now What" format?

Output Requirements:
- If the summary meets all criteria perfectly, output exactly: PASSED
- If there are errors, output a CORRECTIVE MEMO listing specific, actionable bullet points for the Architect to fix. Do NOT rewrite the summary yourself."""

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", reflection_sys_prompt),
        MessagesPlaceholder(variable_name='messages')
    ]
)

generation_sys_prompt = """You are the Lead Clinical Document Architect for CliniClarity. Your mission is to transform dense medical documentation into accessible, 6th-grade-level health insights.

Your Constraints:
1. Structure: You must use the "What, So What, Now What" framework.
2. Language: Avoid all clinical jargon; if a term is essential, explain it in simple terms immediately.
3. Grounding: Only include information explicitly found in the provided document.

Iteration Instructions:
Look at the message history. If you receive a CORRECTIVE MEMO from the Auditor, you must output a revised summary that specifically addresses every flagged issue while maintaining the required format."""

generation_prompt = ChatPromptTemplate.from_messages([
    ("system", generation_sys_prompt),
    MessagesPlaceholder(variable_name="messages")
])

model = init_chat_model(model='gemini-3.1-flash-lite-preview', model_provider='google_genai', temperature=0.0)

class AuditEvaluator(BaseModel):
    is_approved:bool = Field(description="True if the summary has no jargon and no hallucinations.")
    corrective_memo:str = Field(description="If is_approved is False, list the exact bullet points to fix. If True, output 'PASSED'.")

evaluator_model = model.with_structured_output(AuditEvaluator)

generation = generation_prompt | model
reflection = reflection_prompt | evaluator_model
