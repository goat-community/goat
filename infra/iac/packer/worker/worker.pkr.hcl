variable "ami_name" {
  type = string
  default = "goat-worker"
}

variable "source_ami" {
  type = string
  default = "ami-0e067cc8a2b58de59" //Canonical, Ubuntu, 20.04 LTS
}

// Only for creating AMI. This will be destroyed after AMI creation.
variable "instance_type" {
  default = "t2.micro" 
  type = string
}

variable "region" {
  type = string
  default = "eu-central-1"
}


variable "ssh_username" {
  type = string
  default = "ubuntu"
}

packer {
  required_plugins {
    amazon = {
      version = "1.2.1"
      source = "github.com/hashicorp/amazon"
    }
  }
}

// AMI Builder (EBS backed)
// https://www.packer.io/docs/builders/amazon/ebs
source "amazon-ebs" "worker" {
  ami_name      = var.ami_name
  source_ami    = var.source_ami
  instance_type = var.instance_type
  region        = var.region
  ssh_username  = var.ssh_username
  force_deregister = true
  force_delete_snapshot = true
}

build {
  name = "goat"
  sources = ["source.amazon-ebs.worker"]

  provisioner "shell" {
    script = "./bootstrap.sh"
  }
}