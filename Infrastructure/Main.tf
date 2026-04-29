locals {
  services = ["compute.googleapis.com", "storage.googleapis.com", "cloudkms.googleapis.com",
    "run.googleapis.com", "firebase.googleapis.com", "identitytoolkit.googleapis.com",
    "secretmanager.googleapis.com", "containerscanning.googleapis.com"]
}

resource "google_project_service" "enable_apis" {
  for_each = toset(local.services)
  project  = "cliniclarity"
  service  = each.value
}

resource "google_service_account" "cliniclarity_service_account" {
  account_id   = "cliniclarity-app-service"
  display_name = "CliniClarity Application Identity"
  depends_on = [google_project_service.enable_apis]
}

module "storage" {
  source     = "./Storage"
  depends_on = [google_project_service.enable_apis]
  service_account_email = google_service_account.cliniclarity_service_account.email
}

resource "null_resource" "docker_build_push" {
  # This triggers a rebuild only if the files inside CliniGraph change
  triggers = {
    always_run = timestamp() # Forces a build every time you run terraform apply (Great for dev)
  }

  provisioner "local-exec" {
    command = <<EOT

      echo "torch" >> ./CliniGraph/requirements.txt
      # 1. Authenticate Docker to your GCP region
      gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

      # 2. Build the image using the Dockerfile in the CliniGraph folder
      docker build --platform linux/amd64 --no-cache --provenance=false -t us-central1-docker.pkg.dev/cliniclarity/${module.storage.artifact_repo}/cliniclarity-agent:latest ./CliniGraph

      # 3. Push the image to Artifact Registry
      docker push us-central1-docker.pkg.dev/cliniclarity/${module.storage.artifact_repo}/cliniclarity-agent:latest
    EOT
  }

  # Ensure the registry exists before we try to push to it
  depends_on = [module.storage]
}


module "compute" {
  source     = "./Compute"
  depends_on = [google_project_service.enable_apis, null_resource.docker_build_push]

  google_api_key    = var.google_api_key
  pinecone_api_key  = var.pinecone_api_key
  huggingface_token = var.hugging_face_token
  index             = pinecone_index.serverless.name
  langchain_api_key = var.langchain_api_key
  cache_bucket_name = module.storage.storage_bucket

  google_oauth_client_id = var.google_oauth_client_id
  google_oauth_client_secret = var.google_oauth_client_secret
  service_account_email = google_service_account.cliniclarity_service_account.email
  artifact_repository = module.storage.artifact_repo
  project  = var.project
  display_name = "CliniClarity Web App"
}

import {
  id = "projects/cliniclarity"
  to = module.compute.google_identity_platform_config.auth_config
}