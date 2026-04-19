from transformers import pipeline

try:
    print("🛡️ Loading ProtectAI Prompt Injection Defender...")

    injection_classifier = pipeline(
        "text-classification",
        model="protectai/deberta-v3-base-prompt-injection-v2",
        device=-1 # # -1 forces CPU which is highly stable for testing (device=0 if you have a GPU)
    ) # Load the Prompt Injection Detector ONCE at startup

    print("✅ Security Defender Loaded.")

except Exception as e:
    print(f"🚨 Security Model Failed to Load: {e}")


async def is_prompt_injection(query: str) -> bool:
    """
    Scans the user's query for adversarial prompt injections and jailbreaks.
    Returns True if an attack is detected.
    """ # Doc-String used as metadata

    result = injection_classifier(query) # Run the user's query through the classifier

    label = result[0].get('label') # Label will either be INJECTION or SAFE
    score = result[0].get('score') # The score is between 0 and 1

    print(f"🛡️ Security Scan -> Status: {label} | Confidence: {score:.4f}") # Log the security scan for your audit trail

    return label == "INJECTION" and score > 0.75 # Flag the model when injection is detected