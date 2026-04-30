# Architecture Decision Record: Infrastructure as Code (IaC) with Terraform

* **Status:** Accepted
* **Date:** 2026-03-16

## Context
To satisfy HIPAA requirements, the cloud environment hosting CliniClarity must be reproducible, version-controlled, and strictly isolated. Manual configuration ("ClickOps") introduces human error and lacks the audit trail necessary for healthcare certification.

## Decision: Utilize Terraform for Multi-Cloud Provisioning
We have selected Terraform to define and deploy the entire CliniClarity stack across GCP ensuring that the infrastructure is treated exactly like application code.

## Decision Rationale
* Declarative Blueprints: HIPAA requires a contingency plan; Terraform allows us to rebuild the entire clinical environment in a new region in minutes if a primary site fails.
* Auditability: Every change to the infrastructure is logged in Git, providing a "Who, What, and When" record for every security group or IAM policy change.
* Least Privilege: We can programmatically enforce that only the CliniClarity-Agent has access to the local redaction logs, preventing unauthorized data exposure

## Alternatives Considered
* **AWS CloudFormation** would have created a dangerous vendor lock-in that prevents the agent from seamlessly utilizing the GCP services you've integrated, breaking the multi-cloud resilience required for a modern healthcare application.
* **Manual Setup (ClickOps)** is a non-starter for HIPAA because it provides no verifiable audit trail, relies entirely on human memory for security configurations, and makes it impossible to mathematically prove that the production environment is identical to the tested secure environment.
