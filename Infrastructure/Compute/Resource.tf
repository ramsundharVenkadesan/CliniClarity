resource "google_project_iam_member" "firebase_admin" {
  project = "cliniclarity"
  role    = "roles/firebaseauth.admin"
  member  = "serviceAccount:${var.service_account_email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = "cliniclarity"
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${var.service_account_email}"
}


resource "google_cloud_run_v2_service" "cliniclarity_api" {
  name     = var.cloud_run
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  deletion_protection = false



  template {
    service_account = var.service_account_email

    timeout = "300s"

    containers {
      image = "us-central1-docker.pkg.dev/cliniclarity/${var.artifact_repository}/cliniclarity-agent:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      env {
        name  = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.api_keys["google-api-key"].secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "INDEX_NAME"
        value = var.index
      }
      env {
        name  = "LANGCHAIN_API_KEY"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.api_keys["langchain-api-key"].secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "LANGCHAIN_PROJECT"
        value = "cliniclarity-production"
      }

      env {
        name  = "HF_TOKEN"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.api_keys["huggingface-token"].secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "PINECONE_API_KEY"
        value_source {
          secret_key_ref {
            secret = google_secret_manager_secret.api_keys["pinecone-api-key"].secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "CACHE_BUCKET_NAME"
        value = var.cache_bucket_name
      }

      env {
        name  = "DEEPEVAL_TELEMETRY_OPT_OUT"
        value = "YES"
      }
      env {
        name  = "LANGCHAIN_TRACING_V2"
        value = "true"
      }

      env {
        name  = "FIREBASE_API_KEY"
        value = data.google_firebase_web_app_config.app_config.api_key
      }
      env {
        name  = "FIREBASE_AUTH_DOMAIN"
        value = data.google_firebase_web_app_config.app_config.auth_domain
      }

      env {
        name  = "LANGCHAIN_ENDPOINT"
        value = "https://api.smith.langchain.com"
      }


    }
  }
  lifecycle {
    ignore_changes = [
      template.0.containers.0.image,
      client,
      client_version
    ]
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = google_cloud_run_v2_service.cliniclarity_api.project
  location = google_cloud_run_v2_service.cliniclarity_api.location
  name     = google_cloud_run_v2_service.cliniclarity_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
