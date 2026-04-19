terraform {
  required_version = "~>1.14.0"

  backend "gcs" {
    bucket = "cliniclarity-tf-state"
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
  region  = "us-central1"
  project = "cliniclarity"
}