terraform {
  required_version = "~>1.14.0"

  backend "gcs" {
    bucket = "cliniclarity-tf-state-2"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~>7.27.0"
    }
    pinecone = {
      source  = "pinecone-io/pinecone"
      version = "3.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.8.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.0"
    }
  }
}

provider "pinecone" {
  api_key = var.pinecone_api_key
}
provider "random" {}

provider "google" {
  region                = var.region
  project               = var.project
  billing_project       = var.billing_project
  user_project_override = true
}

provider "google-beta" {
  region                = var.region
  project               = var.project
  billing_project       = var.billing_project
  user_project_override = true

}