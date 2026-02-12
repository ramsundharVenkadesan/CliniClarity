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

resource "aws_lambda_permission" "allow_s3" {
  statement_id = "AllowS3Invoke"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal = "s3.amazonaws.com"
  source_arn = aws_s3_bucket.patient_data.arn
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
    actions = ["textract:*"]
    resources = ["*"]
  }
  statement {
    sid = "ComprehendMedicalAccess"
    effect = "Allow"
    actions = ["comprehendmedical:*"]
    resources = ["*"]
  }
  statement {
    sid       = "CloudWatchLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.lambda_log_group.arn}:*"]
  }
}

resource "aws_iam_role" "function_execution" {
  name = var.lambda_execution_role
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/data_preparation_lambda"
  retention_in_days = 14
}

resource "aws_iam_role_policy" "function_permissions" {
  name = "MedicalDocumentProcessingPolicy"
  role = aws_iam_role.function_execution.id
  policy = data.aws_iam_policy_document.lambda_processing.json
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.patient_data.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda_function.arn
    events = ["s3:ObjectCreated:*"]
    filter_suffix = ".pdf"
  }
  depends_on = [aws_lambda_permission.allow_s3]
}