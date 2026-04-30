# CliniClarity 🩺 - Deployment Guide

CliniClarity is a serverless, AI-powered medical document assistant built with Python, FastAPI, LangGraph, and Firebase. This guide provides step-by-step instructions on how to deploy the full infrastructure to Google Cloud Platform (GCP) using Terraform.

---

## 🛠 Prerequisites

Before deploying, ensure you have the following installed and configured on your local machine:

1. **[Terraform CLI](https://developer.hashicorp.com/terraform/downloads)** (v1.0+)
2. **[Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install)**
3. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Must be running during deployment for Terraform to build and push the container)

You will also need active accounts and API keys for the following services:
* **Google Cloud Platform:** A project with billing enabled.
* **Firebase:** A project linked to your GCP project.
* **Pinecone:** A serverless vector database index (Dimensionality: `1536`).
* **Google AI Studio:** A Gemini API key.
* **HuggingFace:** An access token (for the prompt-injection security scanner).
* **LangSmith / LangChain:** An API key for agent tracing and observability.

---

## 🛠️ Phase 0: Human-in-the-Loop (HITL) Manual Setup
Terraform automates the "wires," but Google requires manual verification for identity and legal steps. You must complete these steps before running the automation:  

1. **Create a GCP Project:** Manually create a new project in the Google Cloud Console.  
2. **Link Billing:** Ensure an active billing account is attached to the project.  
3. **OAuth Consent Screen:** Navigate to **APIs & Services** > **OAuth consent screen**.
    * Configure the screen (Internal/External), add your support email, and include the `auth/userinfo.email` and `auth/userinfo.profile` scopes.  
4. **Generate OAuth Credentials:**
    * Navigate to **APIs & Services** > **Credentials**.
    * Create an **OAuth 2.0 Client ID** (Web Application).
    * Note your **Client ID** and **Client Secret** for Step 2.

----

## 🚀 Step 1: Local Authentication

First, authenticate your local machine with Google Cloud and Docker so Terraform has the permissions it needs to build and deploy. Open your terminal and run:

```bash
gcloud auth login # 1. Login to Google Cloud

gcloud auth application-default login # 2. Set your default application credentials for Terraform

gcloud config set project YOUR_GCP_PROJECT_ID # 3. Set your active GCP project
```

---

## 🔐 Step 2: Configure Environment Variables
The Terraform configuration requires several sensitive API keys. **Do not hardcode these.** Instead, create a `terraform.tfvars` file in the root of your project.

1. Create the file: `touch terraform.tfvars`
2. Add your keys to `terraform.tfvars`
```
google_api_key               = "AIzaSyYourGoogleApiKeyHere..."
pinecone_api_key             = "your-pinecone-api-key"
hugging_face_token           = "hf_YourHuggingFaceToken"
langchain_api_key            = "ls__YourLangchainKey"
pinecone                     = "index"
google_oauth_client_id       = "your-oauth-client-id.apps.googleusercontent.com"
google_oauth_client_secret   = "your-oauth-client-secret"
project                      = "GCP-Project"
```
_(Note: Ensure terraform.tfvars is added to your `.gitignore` file so you don't accidentally commit it to GitHub!)_

---

## 🪣 Step 3: Configure Terraform State Bucket
Terraform uses a "backend" to track the state of your infrastructure. Because GCS backend blocks do not accept variables, you must manually update this before initializing.
1. Create a standard Google Cloud Storage bucket in your GCP console to hold your state file.
2. Open the `Terraform.tf` file in your code editor.
3. Locate the backend "gcs" block at the top of the file.
4. Replace the hardcoded `bucket` name with your newly created, globally unique bucket name.

_(Note: If you are just deploying a test instance for yourself, you can simply delete the entire backend `"gcs" { ... } block` to store the state locally on your machine instead)._

---

## 🏗 Step 4: Pre-Deployment Check & Deploy

### ⚠️ Important: Handling Identity Platform Imports

At the bottom of `Main.tf`, there is an `import` block for `google_identity_platform_config`.  
   * **If you are using a Brand New Account/Project:** You **MUST** comment out or delete this import block. Terraform cannot `import` a resource that does not exist yet; it will create it fresh during the deployment.  
   * **If you are redeploying to an Existing Project:** Keep the `import` block active to ensure Terraform syncs with your existing Firebase identity settings.

Once the check is complete and Docker is running, you are ready to deploy. With your variables set and Docker running, you are ready to deploy. Terraform will use the committed `requirements.txt` file to build the Docker container deterministically, push it to GCP Artifact Registry, and deploy the Cloud Run service.
```bash
terraform init # 1. Initialize Terraform (downloads required providers)

terraform plan # 2. Review the deployment plan

terraform apply # 3. Apply the infrastructure (type 'yes' when prompted)
```
Deployment typically takes 5 to 8 minutes. Once complete, Terraform will output your live Cloud Run URL.

---

## 🔥 Step 5: Post-Deployment Firebase Setup
Because CliniClarity uses Firebase Authentication as a strict security gate, you must whitelist your new Cloud Run URL; otherwise, logins will be blocked with an `auth/unauthorized-domain` error.

1. Open the **[Firebase Console](https://console.firebase.google.com/u/0/)**.
2. Navigate to Authentication > Settings > Authorized domains.
3. Click **Add domain**.
4. Paste your exact Cloud Run URL (e.g., `cliniclarity-api-xyz-uc.a.run.app`) without the `https://` or trailing slashes.
5. Click Add.

_You must also ensure that Email/Password and Google Sign-In are enabled in the "Sign-in method" tab of Firebase Authentication._

---

## 🧹 Destroying the Infrastructure
If you need to tear down the environment to stop incurring costs, simply run: `terraform destroy`

_(Type 'yes' when prompted. Note: You may need to manually empty the GCP Storage Buckets before Terraform can successfully delete them)._

