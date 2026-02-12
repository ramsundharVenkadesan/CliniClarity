# ADR 002: Adoption of Python Runtime for PDF Redaction Service

* **Status:** Accepted
* **Date:** 2026-02-09
* **Context:**
    The CliniClarity platform requires a "Redaction Service" to sanitize Protected Health Information (PHI) from patient documents. The workflow involves:
    1.  Ingesting raw PDFs from S3.
    2.  Extracting text coordinates using AWS Textract.
    3.  Identifying PHI entities using Amazon Comprehend Medical.
    4.  **Drawing permanent black boxes** over specific coordinates in the original PDF file to ensure non-reversible redaction.

    We evaluated **Go** and **Python** for the AWS Lambda runtime to handle this specific task.

* **Decision:**
    We will use **Python 3.8** for the Redaction Lambda function, utilizing the `PyMuPDF` (fitz) library for PDF manipulation and `boto3` for AWS SDK interactions.

* **Detailed Rationale:**
    1.  **Library Maturity (The Primary Driver):**
        The core requirement is "coordinate-based redaction" (drawing shapes at specific X,Y locations).
        * **Python:** The `PyMuPDF` library provides a robust `page.add_redact_annot()` method that physically removes underlying text and rasterizes the redaction area. This is critical for HIPAA compliance to prevent "copy-paste" leaks under black boxes.
        * **Go:** While Go has PDF libraries (e.g., `unidoc`), they are often commercial/licensed or lack mature "destructive redaction" capabilities comparable to PyMuPDF's open-source feature set.

    2.  **AWS Integration:**
        The `boto3` library in Python provides first-class support for the complex JSON structures returned by `Textract` and `ComprehendMedical`. Parsing nested JSON blocks for "BoundingBox" geometries is significantly more verbose in Go (requires struct mapping) compared to Python's dynamic dict handling.

    3.  **Prototyping Velocity:**
        Python allowed for rapid iteration of the "OCR-to-Redaction" loop. Given the strict deadline for the MVP, the development speed of Python outweighed the execution speed of Go.

* **Consequences:**
    * **Positive:**
        * **Code Simplicity:** The entire redaction logic fits in approximately 50 lines of code, making it highly maintainable.
        * **Maintenance:** Future engineers (or data scientists) can easily modify the logic as Python is the standard language for AI/ML pipelines.
    * **Negative:**
        * **Cold Start Latency:** Python runtimes on AWS Lambda have slower cold starts than Go.
        * **Deployment Size:** The `PyMuPDF` library requires binary dependencies (`manylinux` wheels), increasing the Lambda package size.
    * **Mitigation Strategy:**
        * We implemented **AWS Lambda Layers** in Terraform (`main.tf`) to isolate the heavy `PyMuPDF` dependency from the application logic. This keeps the function deployment lightweight and allows for caching the layer.
        * We pinned the Python version to `3.8` and utilized `manylinux2014_x86_64` wheels to ensure binary compatibility with the AWS Lambda environment.
