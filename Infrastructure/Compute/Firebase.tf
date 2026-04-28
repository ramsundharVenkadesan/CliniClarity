resource "google_firebase_project" "cliniclarity_firebase" {
  provider = google-beta
  project  = "cliniclarity"
}

resource "google_identity_platform_config" "auth_config" {
  provider = google-beta
  project  = "cliniclarity"

  sign_in {
    allow_duplicate_emails = false
    email {
      enabled           = true
      password_required = true
    }
  }

  depends_on = [google_firebase_project.cliniclarity_firebase]
}

resource "google_identity_platform_default_supported_idp_config" "google_sign_in" {
  provider      = google-beta
  project       = "cliniclarity"
  enabled       = true
  idp_id        = "google.com"
  client_id     = var.google_oauth_client_id
  client_secret = var.google_oauth_client_secret

  depends_on = [google_identity_platform_config.auth_config]
}

resource "google_firebase_web_app" "cliniclarity_web_app" {
  provider     = google-beta
  project      = "cliniclarity"
  display_name = "CliniClarity Web App"
  depends_on   = [google_firebase_project.cliniclarity_firebase]
}

data "google_firebase_web_app_config" "app_config" {
  provider   = google-beta
  project    = "cliniclarity"
  web_app_id = google_firebase_web_app.cliniclarity_web_app.app_id
}
