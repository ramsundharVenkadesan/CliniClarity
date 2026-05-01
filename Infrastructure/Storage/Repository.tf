resource "google_artifact_registry_repository" "registry" {
  project = var.project
  location = var.region
  repository_id = var.registry_id
  format = "DOCKER"
}
