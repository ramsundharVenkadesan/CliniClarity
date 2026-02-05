terraform { // Terraform code block to connect the configuration to external providers
  required_version = ">=1.0.0" // Terraform Core version that the configuration supports
  backend "s3" {
    bucket = "terraform-state-backend-1608"
    key = "terraform.tfstate"
    region = "us-east-1"
  }
  required_providers { // An inner code block to specify one or more providers required for configuration to run
    aws = { // Amazon Web Services (AWS) provider
      source = "hashicorp/aws" // The provider is sourced from HashiCorp registry
      version = "~> 3.0" // Provider version to be installed
    }
  }
}

provider "aws" { // Configuring AWS provider
  region = "us-east-1" // Region argument to specify where the infrastructure will be deployed
}
