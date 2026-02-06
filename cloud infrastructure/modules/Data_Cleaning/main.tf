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
  name = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
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
    # This command uses Docker to build Linux-compatible binaries on your Mac
    command = <<EOT
      mkdir -p ${path.module}/layer_content/python
      docker run --rm -v ${path.module}/layer_content:/var/task public.ecr.aws/sam/build-python3.8:latest \
        pip install -r /var/task/../requirements.txt -t /var/task/python
    EOT
  }
}

data "archive_file" "layer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/layer_content"
  output_path = "${path.module}/pymupdf_layer.zip"
  depends_on  = [null_resource.build_lambda_layer]
}

resource "aws_lambda_layer_version" "package_layer" {
  filename            = data.archive_file.layer_zip.output_path
  source_code_hash    = data.archive_file.layer_zip.output_base64sha256
  layer_name          = "pymupdf_lib"
  compatible_runtimes = ["python3.8"]
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

data "archive_file" "lambda_file" {
  type = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lamdba_function_payload.zip"
}

resource "aws_lambda_function" "lambda_function" {
  filename = data.archive_file.lambda_file.output_path
  function_name = "data_preparation_lambda"
  role = aws_iam_role.function_execution.arn
  handler = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_file.output_base64sha256
  runtime = "python3.8"

  depends_on = [aws_cloudwatch_log_group.lambda_log_group]

  tags = {
    Env = local.environment
    Project = local.project
    Purpose = "Lambda Function to invoke Textract when a PDF is uploaded to S3"
  }
}