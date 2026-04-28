from langchain.chat_models import init_chat_model # Import function to create and initialize a model
from pydantic import BaseModel, Field # Import Pydantic data-validation package
import logging


dynamic_model = init_chat_model(model="gemini-3-flash-preview", temperature=0.0, model_provider="google_genai") # Create a Gemini-3-Flash model with no creativity

class DocumentValidation(BaseModel): # Define validation schema class
    is_medical: bool = Field(description="True if the text appears to be a medical report, clinical note, or lab result.") # Field that ensures uploaded text is a medical document
    confidence_score: float = Field(description="Confidence from 0 to 1.") # Field to extract a confidence score between 0 and 1
    reasoning: str = Field(description="Short reason why this is or isn't a medical document.") # Field to extract a reason why the uploaded document is or is not a medical document


def is_medical_heuristic(text: str) -> bool: # Generic Function to evaluate the uploaded document for essential markers
    """Fast check for essential medical markers before calling the LLM.""" # Doc-String used as metadata

    medical_keywords = [
        "patient", "physician", "diagnosis", "symptoms", "treatment",
        "clinical", "laboratory", "rx", "medication", "prognosis",
        "medical record", "history of present illness", "icd-10"
    ] # A list of sample medical keywords

    text_lower = text.lower() # Lowercase all the characters
    matches = sum(1 for word in medical_keywords if word in text_lower) # Increment by one for every medical term from source text

    # If at least 3 unique medical keywords are present, it's worth processing
    return matches >= 3 # At least 3 unique medical words are present in the document


async def validate_medical_document(pdf_text: str, model=dynamic_model) -> bool: # Generic function to validate the uploaded document
    """Final gatekeeper check using the LLM for context.""" # Doc-String used as metadata

    if not is_medical_heuristic(pdf_text[:2000]): # Extract first 2000 characters from the uploaded document
        logging.info("🚨 Blocked: Document failed basic medical keyword heuristic.")
        return False # The text failed to satisfy the check

    validation_prompt = f"""
    Analyze the following document snippet. Is this a medical record, clinical summary, or lab report?
    Snippet: {pdf_text[:1000]}

    Return your answer in the required JSON format.
    """ # LLM validation by passing only the first 1000 characters to keep it cheap and efficient

    validator_chain = model.with_structured_output(DocumentValidation) # The model's response must fit the schema defined above
    result = await validator_chain.ainvoke(validation_prompt) # Asynchronous invocation of the LLM

    logging.info(f"🔍 Validator Result: Medical={result.is_medical} (Conf: {result.confidence_score}) | Reason: {result.reasoning}")

    return result.is_medical and result.confidence_score > 0.8 # Final to determine whether checks have passed