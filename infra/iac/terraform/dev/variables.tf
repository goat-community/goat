variable "hcloud_token" {
  type        = string
  sensitive   = true
  description = "Hetzner Cloud API token"
}

variable "aws_region" {
  type        = string
  default     = "eu-central-1"
  description = "AWS region"
}

variable "aws_access_key" {
  type        = string
  sensitive   = true
  description = "AWS access key"
}

variable "aws_secret_key" {
  type        = string
  sensitive   = true
  description = "AWS secret key"
}

variable "hcloud_postgresql_data_volume" {
  default     = "plan4better-postgres-dev-geonode-data"
  description = "Name of the Hetzner Cloud volume to use for the PostgreSQL data. This volume must exist and it will be attached to the PostgreSQL server."
}

variable "s3_backup_bucket" {
  default     = "plan4better-hetzner-backup-dev"
  description = "Name of the S3 bucket to use for backups. This bucket must exist and the PostgreSQL server will upload backups to it."
}

variable "db_ssh_public_key" {
  default = "~/.ssh/dev_db.pub"
  description = "Path to the public key to use for SSH access to the PostgreSQL server."
}

variable "kube_hetzner_ssh_private_key" {
  default = "~/.ssh/dev_kube_hetzner"
  description = "Path to the private key to use for SSH access to the Kubernetes cluster."
}

variable "kube_hetzner_ssh_public_key" {
  default = "~/.ssh/dev_kube_hetzner.pub"
  description = "Path to the public key to use for SSH access to the Kubernetes cluster."
}
