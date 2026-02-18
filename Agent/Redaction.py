from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def redact_pii(text: str) -> str:
    # 1. Analyze the text for PII entities (Name, Phone, Email, Location, etc.)
    results = analyzer.analyze(text=text, entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION", "DATE_TIME"],
                               language='en')

    # 2. Anonymize the identified entities
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )
    return anonymized_result.text