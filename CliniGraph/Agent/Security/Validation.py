from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

dynamic_model = init_chat_model(model="gemini-3-flash-preview", temperature=0.0, model_provider="google_genai")


# 1. Define the Validation Schema
class DocumentValidation(BaseModel):
    is_medical: bool = Field(
        description="True if the text appears to be a medical report, clinical note, or lab result.")
    confidence_score: float = Field(description="Confidence from 0 to 1.")
    reasoning: str = Field(description="Short reason why this is or isn't a medical document.")


def is_medical_heuristic(text: str) -> bool:
    """Fast check for essential medical markers before calling the LLM."""
    medical_keywords = [
        "patient", "physician", "diagnosis", "symptoms", "treatment",
        "clinical", "laboratory", "rx", "medication", "prognosis",
        "medical record", "history of present illness", "icd-10"
    ]
    text_lower = text.lower()
    matches = sum(1 for word in medical_keywords if word in text_lower)

    # If at least 3 unique medical keywords are present, it's worth processing
    return matches >= 3


async def validate_medical_document(pdf_text: str, model=dynamic_model) -> bool:
    """Final gatekeeper check using the LLM for context."""

    # Tier 1: Fast Heuristic (Saves Cost)
    if not is_medical_heuristic(pdf_text[:2000]):
        print("🚨 Blocked: Document failed basic medical keyword heuristic.")
        return False

    # Tier 2: LLM Validation (High Accuracy)
    # We only send the first 1000 characters to keep it fast and cheap
    validation_prompt = f"""
    Analyze the following document snippet. Is this a medical record, clinical summary, or lab report?
    Snippet: {pdf_text[:1000]}

    Return your answer in the required JSON format.
    """

    validator_chain = model.with_structured_output(DocumentValidation)
    result = await validator_chain.ainvoke(validation_prompt)

    print(f"🔍 Validator Result: Medical={result.is_medical} (Conf: {result.confidence_score})")

    return result.is_medical and result.confidence_score > 0.8