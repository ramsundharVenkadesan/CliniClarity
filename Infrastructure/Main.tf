locals { // Locals Code-Block
  services = ["compute.googleapis.com", "storage.googleapis.com", "cloudkms.googleapis.com",
    "run.googleapis.com", "firebase.googleapis.com", "identitytoolkit.googleapis.com",
    "secretmanager.googleapis.com", "containerscanning.googleapis.com",
  "cloudresourcemanager.googleapis.com", "artifactregistry.googleapis.com"] // List of services to enable
}

resource "google_project_service" "enable_apis" { // Resource block to enable all APIs
  for_each = toset(local.services)
  project  = var.project
  service  = each.value
}

resource "google_service_account" "cliniclarity_service_account" { // Resource block to create a service account
  account_id   = "cliniclarity-app-service"
  display_name = "CliniClarity Application Identity"
  depends_on   = [google_project_service.enable_apis]
}

module "storage" { // Module block to create storage infrastructure
  source                = "./Storage"
  depends_on            = [google_project_service.enable_apis]
  service_account_email = google_service_account.cliniclarity_service_account.email
  project               = var.project
}

resource "null_resource" "docker_build_push" { // Null resource to build and push Docker image of the AI Agent

  triggers = {               // Triggers a rebuild when files inside AI Agent changes
    always_run = timestamp() // Forces a build every time you run Terraform Apply
  }

  provisioner "local-exec" {
    command = <<EOT
      gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

      docker build --platform linux/amd64 --no-cache --provenance=false -t us-central1-docker.pkg.dev/${var.project}/${module.storage.artifact_repo}/cliniclarity-agent:latest ./CliniGraph

      docker push us-central1-docker.pkg.dev/${var.project}/${module.storage.artifact_repo}/cliniclarity-agent:latest
    EOT
  }

  depends_on = [module.storage] // Manual dependency to ensure artifact registry exists before pushing
}

resource "null_resource" "firebase_user_purge" { // Null resource to destroy all identities in Firebase
  provisioner "local-exec" {
    when    = destroy
    command = "python3 Purge_Users.py"
  }

}


module "compute" { // Module block to create compute infrastructure
  source     = "./Compute"
  depends_on = [google_project_service.enable_apis, null_resource.docker_build_push]

  google_api_key    = var.google_api_key
  pinecone_api_key  = var.pinecone_api_key
  huggingface_token = var.hugging_face_token
  index             = pinecone_index.serverless.name
  langchain_api_key = var.langchain_api_key
  cache_bucket_name = module.storage.storage_bucket

  google_oauth_client_id     = var.google_oauth_client_id
  google_oauth_client_secret = var.google_oauth_client_secret
  service_account_email      = google_service_account.cliniclarity_service_account.email
  artifact_repository        = module.storage.artifact_repo
  project                    = var.project
  display_name               = "CliniClarity Web App"
}

import { // Import block to import an existing auth-config for Firebase
  id = "projects/${var.project}"
  to = module.compute.google_identity_platform_config.auth_config
} // Comment this block out, if the GCP project is brand new