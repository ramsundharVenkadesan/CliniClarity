resource "random_id" "keyring_suffix" {
  byte_length = 4
}

# 2. Attach the random string to the KeyRing name!
resource "google_kms_key_ring" "key_ring" {
  name     = "cliniclarity-cache-keyring-${random_id.keyring_suffix.hex}"
  location = "us"
}

resource "google_kms_crypto_key" "cache_key" {
  name = var.kms_key
  key_ring = google_kms_key_ring.key_ring.id
  rotation_period = "776000s"
}

data "google_storage_project_service_account" "gcs_account" {}

resource "google_kms_crypto_key_iam_binding" "gcs_cmek_binding" {
  crypto_key_id = google_kms_crypto_key.cache_key.id
  role = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  members = ["serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"]
}

