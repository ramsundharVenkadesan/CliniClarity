resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket_iam_member" "cache_bucket_access" {
  bucket = google_storage_bucket.cache_storage.name
  role = "roles/storage.objectUser"
  member = "serviceAccount:${var.service_account_email}"
}

resource "google_storage_bucket" "cache_storage" {
  name = "cliniclarity-doc-hash-${random_id.bucket_suffix.hex}"
  location = "us"

  force_destroy = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 1 }
    action { type = "Delete"}
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.cache_key.id
  }

  depends_on = [google_kms_crypto_key_iam_binding.gcs_cmek_binding]
}
