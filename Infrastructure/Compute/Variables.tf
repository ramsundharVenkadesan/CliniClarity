variable "cloud_run" {
  type    = string
  default = "cliniclarity-api"

  validation {
    condition     = length(var.cloud_run) > 5
    error_message = "Must be a valid name for Cloud-Run service"
  }
}

variable "service_account_email" {
  type = string
}

variable "cliniclarity_vpc" {
  type = string
  default = "cliniclarity-vpc"
}

variable "cliniclarity_subnet" {
  type = string
  default = "cliniclarity-subnet"
}

variable "google_api_key" {
  type = string

  validation {
    condition     = length(var.google_api_key) > 10
    error_message = "Missing Gemini API key"
  }
}
variable "pinecone_api_key" {
  type = string

  validation {
    condition     = length(var.pinecone_api_key) > 10
    error_message = "Missing Pinecone API key"
  }
}

variable "huggingface_token" {
  type = string

  validation {
    condition     = length(var.huggingface_token) > 10
    error_message = "Missing Hugging-Face API key"
  }
}

variable "index" {
  type = string
  validation {
    condition     = length(var.index) > 5
    error_message = "Missing database index"
  }
}
variable "langchain_api_key" {
  type = string

  validation {
    condition     = length(var.langchain_api_key) > 10
    error_message = "Missing LangChain API key"
  }
}
variable "cache_bucket_name" {
  type = string

  validation {
    condition     = length(var.cache_bucket_name) > 5
    error_message = "Missing cache bucket"
  }
}

variable "region" {
  type    = string
  default = "us-central1"
  validation {
    condition     = strcontains(var.region, "-")
    error_message = "A valid region is required to deploy infrastructure"
  }
}

variable "google_oauth_client_id" {
  type = string
}

variable "google_oauth_client_secret" {
  type = string
}


