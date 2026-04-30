from transformers import pipeline
import logging

try:
    injection_classifier = pipeline(
        "text-classification",
        model="protectai/deberta-v3-base-prompt-injection-v2",
        device=-1 # # -1 forces CPU which is highly stable for testing (device=0 if you have a GPU)
    ) # Load the Prompt Injection Detector ONCE at startup
except Exception as e:
    logging.info(f"🚨 Security Model Failed to Load: {e}")


async def is_prompt_injection(query: str) -> bool:
    """
    Scans the user's query for adversarial prompt injections and jailbreaks.
    Returns True if an attack is detected.
    """ # Doc-String used as metadata

    result = injection_classifier(query) # Run the user's query through the classifier

    label = result[0].get('label') # Label will either be INJECTION or SAFE
    score = result[0].get('score') # The score is between 0 and 1


    return label == "INJECTION" and score > 0.75 # Flag the model when injection is detected