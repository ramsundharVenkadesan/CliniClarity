variable "region" {
  type = string
  default = "us-central1"
}

variable "kms_key" {
  type = string
  default = "cache-encryption-key"
}

variable "pinecone" {
  type = string
  default = "patient-data"
}

variable "registry_id" {
  type = string
  default = "cliniclarity-repository"
}

variable "service_account_email" {
  type = string
}

variable "project" {
  type = string
}
