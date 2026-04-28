output "storage_bucket" {
  value = google_storage_bucket.cache_storage.name
}

output "artifact_repo" {
  value = google_artifact_registry_repository.registry.name
}