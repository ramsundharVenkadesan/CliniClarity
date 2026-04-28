output "cloud_run" {
  value = module.compute.cloud_run_url
}

output "keys" {
  value = module.compute.keys_uploaded
}
