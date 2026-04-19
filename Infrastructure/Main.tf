locals {
  services = [
    "compute.googleapis.com",
    "storage.googleapis.com",
    "cloudkms.googleapis.com",
    "run.googleapis.com",
    "firebase.googleapis.com",      # The Firebase linking API
    "identitytoolkit.googleapis.com",
    "secretmanager.googleapis.com",
    "containerscanning.googleapis.com"
  ]
}

resource "google_project_service" "enable_apis" {
  for_each = toset(local.services)
  project  = "cliniclarity"
  service  = each.value
}

resource "google_service_account" "cliniclarity_service_account" {
  account_id   = "cliniclarity-app-service"
  display_name = "CliniClarity Application Identity"
}

module "storage" {
  source     = "./Storage"
  depends_on = [google_project_service.enable_apis]
  service_account_email = google_service_account.cliniclarity_service_account.email
}


module "compute" {
  source     = "./Compute"
  depends_on = [google_project_service.enable_apis]

  google_api_key    = var.google_api_key
  pinecone_api_key  = var.pinecone_api_key
  huggingface_token = var.hugging_face_token
  index             = pinecone_index.serverless.name
  langchain_api_key = var.langchain_api_key
  cache_bucket_name = module.storage.storage_bucket

  google_oauth_client_id = var.google_oauth_client_id
  google_oauth_client_secret = var.google_oauth_client_secret
  service_account_email = google_service_account.cliniclarity_service_account.email
}

