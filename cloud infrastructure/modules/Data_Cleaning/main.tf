resource "aws_s3_bucket" "patient_data" {
  bucket = "patient-data-1608"

  tags = {
    Env = local.environment
    Purpose = "Storing input medical file and redacted output files"
    Project = local.project
  }
}


locals {
  environment = "Data-Preparation"
  project = "CliniClarity"
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_processing"{
  statement {
    sid = "S3Access"
    effect = "Allow"
    actions = ["s3:GetObject", "s3:PutObject", "s3:ListObject"]
    resources = [aws_s3_bucket.patient_data.arn, "${aws_s3_bucket.patient_data.arn}/*"]
  }
  statement {
    sid = "TextractAccess"
    effect = "Allow"
    actions = ["textract:AnalyzeDocument", "textract:GetDocumentAnalysis"]
    resources = ["*"]
  }
  statement {
    sid = "ComprehendMedicalAccess"
    effect = "Allow"
    actions = ["comprehendmedical:DetectPHI"]
    resources = ["*"]
  }
}

resource "aws_iam_role" "function_execution" {
  name = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy" "function_permissions" {
  name = "MedicalDocumentProcessingPolicy"
  role = aws_iam_role.function_execution.id
  policy = data.aws_iam_policy_document.lambda_processing.json
}

data "archive_file" "lambda_file" {
  type = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lamdba_function_payload.zip"
}

resource "aws_lambda_function" "lambda_function" {
  filename = data.archive_file.lambda_file.output_path
  function_name = "data_preparation_lambda"
  role = aws_iam_role.function_execution.arn
  handler = "data_preparation.lambda_handler"
  source_code_hash = data.archive_file.lambda_file.output_base64sha256
  runtime = "python3.8"

  tags = {
    Env = local.environment
    Project = local.project
    Purpose = "Lambda Function to invoke Textract when a PDF is uploaded to S3"
  }
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambd:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal = "s3.amazonaws.com"
  source_arn = aws_s3_bucket.patient_data.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.patient_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda_function.arn
    events = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}