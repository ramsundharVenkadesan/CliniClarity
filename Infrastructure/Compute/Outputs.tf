output "cloud_run_url" {
  value     = google_cloud_run_v2_service.cliniclarity_api.uri
  sensitive = false
}

output "keys_uploaded" {
  value     = [for secret in google_secret_manager_secret.api_keys : secret.secret_id]
  sensitive = false
}