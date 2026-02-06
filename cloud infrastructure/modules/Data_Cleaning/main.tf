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

resource "local_file" "requirements" {
  content  = "pymupdf"
  filename = "${path.module}/requirements.txt"
}

resource "null_resource" "build_lambda_layer" {
  triggers = {
    requirements_hash = md5(local_file.requirements.content)
  }

  provisioner "local-exec" {
    command = <<EOT
      mkdir -p ${path.module}/layer_content/python
      docker run --rm -v ${path.module}/layer_content:/var/task public.ecr.aws/sam/build-python3.8:latest \
        pip install -r /var/task/../requirements.txt -t /var/task/python
    EOT
  }

  depends_on = [local_file.requirements]
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
  statement {
    sid       = "AllowLogging"
    effect    = "Allow"
    actions   = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
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

data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/layer_content"
  output_path = "${path.module}/pymupdf_layer.zip"

  depends_on = [null_resource.build_lambda_layer]
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.layer_zip.output_path # You will create this file in the next step
  layer_name          = "pymupdf_lib"
  source_code_hash = data.archive_file.layer_zip.output_base64sha256
  compatible_runtimes = ["python3.8"] # Matches your function runtime [cite: 3]
  description         = "Layer containing PyMuPDF (fitz)"
}

resource "aws_lambda_function" "lambda_function" {
  filename = data.archive_file.lambda_file.output_path
  function_name = "data_preparation_lambda"
  role = aws_iam_role.function_execution.arn
  handler = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_file.output_base64sha256
  runtime = "python3.8"

  layers = [aws_lambda_layer_version.package_layer.arn]

  tracing_config {
    mode = "Active"
  }

  tags = {
    Env = local.environment
    Project = local.project
    Purpose = "Lambda Function to invoke Textract when a PDF is uploaded to S3"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_xray" {
  role       = aws_iam_role.function_execution.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"
  retention_in_days = 14
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id = "AllowExecutionFromS3Bucket"
  action = "lambda:InvokeFunction"
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

