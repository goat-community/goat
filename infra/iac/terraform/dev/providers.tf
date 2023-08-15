terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = ">=1.38.1"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">=5.9.0"
    }
  }
  backend "s3" { }
}

provider "hcloud" {
  token = var.hcloud_token
}

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

