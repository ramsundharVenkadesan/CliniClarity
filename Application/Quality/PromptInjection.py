from transformers import pipeline


# 1. Load the Prompt Injection Detector ONCE at startup
# We use a specialized, locally-running NLP model trained on thousands of known jailbreaks.
try:
    print("🛡️ Loading ProtectAI Prompt Injection Defender...")
    injection_classifier = pipeline(
        "text-classification",
        model="protectai/deberta-v3-base-prompt-injection-v2",
        # device=0 if you have a GPU, -1 forces CPU which is highly stable for testing
        device=-1
    )
    print("✅ Security Defender Loaded.")
except Exception as e:
    print(f"🚨 Security Model Failed to Load: {e}")


async def is_prompt_injection(query: str) -> bool:
    """
    Scans the user's query for adversarial prompt injections and jailbreaks.
    Returns True if an attack is detected.
    """
    # Run the user's query through the classifier
    result = injection_classifier(query)

    # The result looks like: [{'label': 'INJECTION', 'score': 0.98}] or [{'label': 'SAFE', 'score': 0.99}]
    label = result[0]['label']
    score = result[0]['score']

    # Log the security scan for your audit trail
    print(f"🛡️ Security Scan -> Status: {label} | Confidence: {score:.4f}")

    # If the model detects an injection with high confidence, flag it
    return label == "INJECTION" and score > 0.75