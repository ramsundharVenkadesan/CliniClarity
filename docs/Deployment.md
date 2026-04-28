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

---

##🔐 Step 2: Configure Environment Variables
The Terraform configuration requires several sensitive API keys. **Do not hardcode these.** Instead, create a `terraform.tfvars` file in the root of your project.

