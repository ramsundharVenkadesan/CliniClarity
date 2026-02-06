import boto3
from fastapi import FastAPI, UploadFile, File, HTTPException
from botocore.exceptions import NoCredentialsError
import os

app = FastAPI()

# AWS Configuration (Use environment variables in production!)
S3_BUCKET_NAME = "patient-data-1608"
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = "us-east-1"

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION
)


@app.post("/upload-pdf/")
async def upload_pdf_to_s3(file: UploadFile = File(...)):
    # 1. Validate File Type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    try:
        # 2. Upload directly to S3
        # We use file.file (the file-like object) directly
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            file.filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        return {
            "message": "Upload successful",
            "filename": file.filename,
            "bucket": S3_BUCKET_NAME
        }

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))