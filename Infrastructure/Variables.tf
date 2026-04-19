variable "region" {
  type    = string
  default = "us-central1"
}

variable "pinecone" {
  type    = string
  default = "patient-data"
}

variable "cloud" {
  type    = string
  default = "aws"

  validation {
    condition     = contains(["aws", "gcp", "azure"], var.cloud)
    error_message = "Must be a valid cloud provider"
  }
}

variable "pinecone_region" {
  type    = string
  default = "us-east-1"
  validation {
    condition     = strcontains(var.pinecone_region, "-")
    error_message = "Must be a valid region"
  }
}

variable "pinecone_api_key" { type = string }
variable "google_api_key" { type = string }
variable "langchain_api_key" { type = string }
variable "hugging_face_token" { type = string }

variable "google_oauth_client_id" { type = string }
variable "google_oauth_client_secret" { type = string }