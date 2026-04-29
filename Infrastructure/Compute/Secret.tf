locals {
  secrets_map = {
    "google-api-key"    = var.google_api_key
    "langchain-api-key" = var.langchain_api_key
    "huggingface-token" = var.huggingface_token
    "pinecone-api-key"  = var.pinecone_api_key
  }
}

resource "google_secret_manager_secret" "api_keys" {
  for_each  = local.secrets_map
  secret_id = each.key
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "api_key_data" {
  secret      = google_secret_manager_secret.api_keys[each.key].id
  for_each    = local.secrets_map
  secret_data = each.value
}
