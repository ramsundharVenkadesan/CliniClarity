resource "aws_s3_bucket" "patient-data" {
  bucket = var.bucket_name
}

resource "aws_lambda_function" "lambda_function" {
  filename = data.archive_file.lambda_file.output_path
  function_name = "data_preparation_lambda"
  role = aws_iam_role.function_execution.arn
  handler = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_file.output_base64sha256
  runtime = "python3.8"

  depends_on = [aws_cloudwatch_log_group.lambda_log_group]
}