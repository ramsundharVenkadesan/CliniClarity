import boto3
import urllib.parse
import json

textract = boto3.client('textract')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        response = textract.detect_document_text(Document={'S3Object': {'Bucket': bucket, 'Name': key}}, FeatureTypes=['LAYOUT', 'FORMS'])
        job_id = response['JobId']
        print(f"Successfully started Textract Job: {job_id} for file: {key}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Textract Job Started Successfully', 'jobId': job_id, 'File': key})
        }
    except Exception as e:
        print(f"Error starting Textract for {key}: {str(e)}")
        raise e