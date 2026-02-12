variable "bucket_name" {
  type = string
  description = "An unique name for Input/Output bucket"
}

variable "lambda_execution_role" {
  type = string
  description = "IAM role attached to the Lambda Function. This governs both who / what can invoke your Lambda Function, as well as what resources our Lambda Function has access to."
  default = "lambda_execution_role"
}