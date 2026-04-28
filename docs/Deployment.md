# CliniClarity 🩺 - Deployment Guide

CliniClarity is a serverless, AI-powered medical document assistant built with Python, FastAPI, LangGraph, and Firebase. This guide provides step-by-step instructions on how to deploy the full infrastructure to Google Cloud Platform (GCP) using Terraform.

---

## 🛠 Prerequisites

Before deploying, ensure you have the following installed and configured on your local machine:

1. **[Terraform CLI](https://developer.hashicorp.com/terraform/downloads)** (v1.0+)
2. **[Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install)**
3. **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Must be running during deployment for Terraform to build and push the container)
4. **Git**

You will also need active accounts and API keys for the following services:
* **Google Cloud Platform:** A project with billing enabled.
* **Firebase:** A project linked to your GCP project.
* **Pinecone:** A serverless vector database index (Dimensionality: `1536`).
* **Google AI Studio:** A Gemini API key.
* **HuggingFace:** An access token (for the prompt-injection security scanner).
* **LangSmith / LangChain:** An API key for agent tracing and observability.

---

## 🚀 Step 1: Local Authentication

First, authenticate your local machine with Google Cloud and Docker so Terraform has the permissions it needs to build and deploy. Open your terminal and run:

```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set your default application credentials for Terraform
gcloud auth application-default login

# 3. Set your active GCP project
gcloud config set project YOUR_GCP_PROJECT_ID
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
google_oauth_client_id       = "your-oauth-client-id.apps.googleusercontent.com"
google_oauth_client_secret   = "your-oauth-client-secret"
```
_(Note: Ensure terraform.tfvars is added to your `.gitignore` file so you don't accidentally commit it to GitHub!)_

---

## 🏗 Step 3: Deploy with Terraform
With your variables set and Docker running, you are ready to deploy. Terraform will use the committed `requirements.txt` file to build the Docker container deterministically, push it to GCP Artifact Registry, and deploy the Cloud Run service.
```bash
terraform init # 1. Initialize Terraform (downloads required providers)

terraform plan # 2. Review the deployment plan

terraform apply # 3. Apply the infrastructure (type 'yes' when prompted)
```
Deployment typically takes 5 to 8 minutes. Once complete, Terraform will output your live Cloud Run URL.

---

## 🔥 Step 4: Post-Deployment Firebase Setup
Because CliniClarity uses Firebase Authentication as a strict security gate, you must whitelist your new Cloud Run URL; otherwise, logins will be blocked with an auth/unauthorized-domain error.

1. Open the Firebase Console.
2. Navigate to Authentication > Settings > Authorized domains.
3. Click Add domain.
4. Paste your exact Cloud Run URL (e.g., cliniclarity-api-xyz-uc.a.run.app) without the https:// or trailing slashes.
5. Click Add.

_You must also ensure that Email/Password and Google Sign-In are enabled in the "Sign-in method" tab of Firebase Authentication._

---

## 🧹 Destroying the Infrastructure
If you need to tear down the environment to stop incurring costs, simply run: `terraform destroy`

_(Type 'yes' when prompted. Note: You may need to manually empty the GCP Storage Buckets before Terraform can successfully delete them)._

