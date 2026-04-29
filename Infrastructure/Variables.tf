variable "region" {
  type    = string
  default = "us-central1"

  validation {
    condition = strcontains(var.region, "-")
    error_message = "Enter a valid GCP region"
  }
}

variable "pinecone" {
  type    = string
  default = "patient-data"
  validation {
    condition = strcontains(var.pinecone, "-")
    error_message = "Enter a valid index name"
  }
}

variable "cloud" {
  type    = string
  default = "aws"

  validation {
    condition     = contains(["aws", "gcp", "azure"], var.cloud)
    error_message = "Must be a valid cloud provider"
  }
}

variable "project" {
  type = string
}

variable "pinecone_region" {
  type    = string
  default = "us-east-1"
  validation {
    condition     = strcontains(var.pinecone_region, "-")
    error_message = "Must be a valid region"
  }
}

variable "pinecone_api_key" {
  type = string
  validation {
    condition = length(var.pinecone_api_key) > 5
    error_message = "Enter a valid Pinecone API key"
  }
}

variable "google_api_key" {
  type = string
  validation {
    condition = length(var.google_api_key) > 5
    error_message = "Enter a valid Gemini API key"
  }
}

variable "langchain_api_key" {
  type = string
  validation {
    condition = length(var.langchain_api_key) > 5
    error_message = "Enter a valid LangSmith API key"
  }
}

variable "hugging_face_token" {
  type = string
  validation {
    condition = length(var.hugging_face_token) > 5
    error_message = "Enter a valid Hugging-Face token"
  }
}

variable "google_oauth_client_id" {
  type = string
  validation {
    condition = length(var.google_oauth_client_id) > 5
    error_message = "Enter a valid Google OAUTH Client ID"
  }
}
variable "google_oauth_client_secret" {
  type = string
  validation {
    condition = length(var.google_oauth_client_secret) > 5
    error_message = "Enter a valid Google OAUTH Client Secret"
  }
}