import boto3
import urllib.parse
import json, time
import fitz
import io

textract = boto3.client('textract')
comprehend_medical = boto3.client('comprehendmedical')
s3 = boto3.client('s3')

def redact_pdf(bucket, key, phi_entities):
    """Physically deletes PII text from the PDF stream."""
    f = io.BytesIO()
    s3.download_fileobj(bucket, key, f)
    doc = fitz.open(stream=f, filetype="pdf")

    for entity in phi_entities:
        target_text = entity['Text']
        for page in doc:
            areas = page.search_for(target_text)
            for area in areas:
                page.add_redact_annot(area, fill=(0, 0, 0))  # Instructions
            page.apply_redactions()  # Destructive removal

    output_buffer = io.BytesIO()
    doc.save(output_buffer, garbage=4, deflate=True)

    clean_key = f"redacted/{key.split('/')[-1]}"
    s3.put_object(Bucket=bucket, Key=clean_key, Body=output_buffer.getvalue())
    return clean_key

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    check_response = None
    job_id = None
    try:
        response = textract.start_document_analysis(Document={'S3Object': {'Bucket': bucket, 'Name': key}}, FeatureTypes=['LAYOUT'])
        job_id = response['JobId']
        print(f"Successfully started Textract Job: {job_id} for file: {key}")

        status = "IN_PROGRESS"

        while status == "IN_PROGRESS":
            time.sleep(5)
            check_response = textract.get_document_analysis(JobId=job_id)
            status = check_response['JobStatus']
        if status == "SUCCEEDED" and check_response:
            full_text = ""
            for block in check_response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    full_text += block['Text'] + ' '
            phi_response = comprehend_medical.detect_phi(Text=full_text[:10000])
            phi_entities = phi_response['Entities']
            print(f"Detected PHI Entities: {phi_entities}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Textract Job Started Successfully', 'jobId': job_id, 'File': key})
        }
    except Exception as e:
        print(f"Error starting Textract for {key}: {str(e)}")
        raise e

