terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = "us-east-1"
  access_key = "test"  # Fake
  secret_key = "test"

  # Endpoints to LocalStack
  endpoints {
    s3       = "http://localhost:4566"
    lambda   = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    sns      = "http://localhost:4566"
    iam      = "http://localhost:4566"
    cloudwatch = "http://localhost:4566"
  }

  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  s3_use_path_style           = true  # Neede this format to S3 in LocalStack
}