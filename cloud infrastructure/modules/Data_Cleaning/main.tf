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

