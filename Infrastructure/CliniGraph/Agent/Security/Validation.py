from langchain.chat_models import init_chat_model # Import function to create and initialize a model
from pydantic import BaseModel, Field # Import Pydantic data-validation package
import logging


dynamic_model = init_chat_model(model="gemini-3-flash-preview", temperature=0.0, model_provider="google_genai") # Create a Gemini-3-Flash model with no creativity

class DocumentValidation(BaseModel): # Define validation schema class
    is_medical: bool = Field(description="True if the text appears to be a medical report, clinical note, or lab result.") # Field that ensures uploaded text is a medical document
    confidence_score: float = Field(description="Confidence from 0 to 1.") # Field to extract a confidence score between 0 and 1
    reasoning: str = Field(description="Short reason why this is or isn't a medical document.") # Field to extract a reason why the uploaded document is or is not a medical document


async def validate_medical_document(pdf_text: str, model=dynamic_model) -> bool: # Generic function to validate the uploaded document
    """Final gatekeeper check using the LLM for context.""" # Doc-String used as metadata


    validation_prompt = f"""
    Analyze the following document snippet. Is this a medical record, clinical summary, or lab report?
    Snippet: {pdf_text[:1000]}

    Return your answer in the required JSON format.
    """ # LLM validation by passing only the first 1000 characters to keep it cheap and efficient

    validator_chain = model.with_structured_output(DocumentValidation) # The model's response must fit the schema defined above
    result = await validator_chain.ainvoke(validation_prompt) # Asynchronous invocation of the LLM

    logging.info(f"🔍 Validator Result: Medical={result.is_medical} (Conf: {result.confidence_score}) | Reason: {result.reasoning}")

    return result.is_medical and result.confidence_score > 0.8 # Final to determine whether checks have passed