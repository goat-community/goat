variable "location" {
  default = "nbg1"
}

variable "instance_name" {
  default = "db-dev"
}

variable "ssh_keys" {
  type        = list(number)
  description = "ssh keys to privision for instance access"
}

variable "server_type" {
  type        = string
  description = "hetzner cloud server type, supports x86 and ARM architectures"
  default     = "cx41"
}

variable "server_image" {
  type        = string
  description = "hetzner cloud server image"
  default     = "debian-12"
}

variable "data_volume" {
  type        = number
  description = "data volume id"
}

variable "backup_volume" {
  type        = string
  description = "backup volume id"
  default     = 0
}


variable "mode" {
  type        = string
  description = "startup mode for the database, can be empty to start the database or 'maintenance' to enable the maintenance mode of the underlying docker container to debug issues see also https://pellepelster.github.io/solidblocks//rds/#maintenance"
  default     = null

  validation {
    condition     = var.mode != null || var.mode != "maintenance"
    error_message = "currently only 'maintenance' or default is supported"
  }
}

variable "backup_s3_bucket" {
  type        = string
  description = "AWS bucket name for S3 backups. To enable S3 backups `backup_s3_bucket`, `backup_s3_access_key` and `backup_s3_secret_key` have to be provided."
  default     = null
}

variable "backup_s3_access_key" {
  type        = string
  description = "AWS access key for S3 backups. To enable S3 backups `backup_s3_bucket`, `backup_s3_access_key` and `backup_s3_secret_key` have to be provided."
  default     = null
}

variable "backup_s3_secret_key" {
  type        = string
  description = "AWS secret key for S3 backups. To enable S3 backups `backup_s3_bucket` `backup_s3_access_key` and `backup_s3_secret_key` have to be provided."
  default     = null
}

variable "backup_full_calendar" {
  type        = string
  description = "systemd timer spec for full backups"
  default     = "*-*-* 20:00:00"
}

variable "backup_incr_calendar" {
  type        = string
  description = "systemd timer spec for incremental backups"
  default     = "*-*-* *:00:55"
}

variable "databases" {
  type        = list(object({ id : string, user : string, password : string }))
  description = "A list of databases to create when the instance is initialized, for example: `{ id : \"database1\", user : \"user1\", password : \"password1\" }`. Changing `user` and `password` is supported at any time, the provided config is translated into an config for the Solidblocks RDS PostgreSQL module (https://pellepelster.github.io/solidblocks/rds/index.html), please see https://pellepelster.github.io/solidblocks/rds/index.html#databases for more details of the database configuration."
}

variable "db_admin_password" {
  type        = string
  description = "password for the database admin user, if not set a random password will be generated"
  default     = null
}

variable "post_script" {
  type        = string
  description = "shell script that will be executed after the server configuration is executed"
  default     = ""
}

variable "pre_script" {
  type        = string
  description = "shell script that will be executed before the server configuration is executed"
  default     = ""
}

variable "labels" {
  type        = map(any)
  description = "A list of labels to be attached to the server instance."
  default     = {}
}

variable "public_net_ipv4_enabled" {
  type        = bool
  description = "enable/disable public ip addresses, see also https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/server#public_net"
  default     = true
}

variable "public_net_ipv6_enabled" {
  type        = bool
  description = "enable/disable public ip addresses, see also https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs/resources/server#public_net"
  default     = true
}

variable "network_id" {
  type        = number
  description = "network the created sever should be attached to, network_ip also needs to bet set in that case"
  default     = null
}

variable "network_ip" {
  type        = string
  description = "ip address in the attached network"
  default     = null
}

variable "ssl_enable" {
  type        = bool
  description = "enable automatic ssl certificate creation using LetsEncrypt"
  default     = false
}

variable "ssl_email" {
  type        = string
  description = "email address to use for LetsEncrypt account creation"
  default     = ""
}

variable "ssl_domains" {
  type        = list(string)
  description = "domains to use for generated certificates"
  default     = []

}

variable "ssl_dns_provider" {
  type        = string
  description = "provider type to use for LetsEncrypt DNS challenge, see https://go-acme.github.io/lego/dns/ for available options"
  default     = ""
}

variable "ssl_dns_provider_config" {
  type        = map(string)
  description = "environment configuration variable(s) to use for DNS provider selected via `ssl_dns_provider`, see documentation of selected provider for required configuration variables"
  default     = {}
}

variable "backup_encryption_passphrase" {
  type        = string
  description = "If set the backups will be encrypted using this passphrase"
  default     = null
}


variable "postgres_docker_image" {
  type        = string
  description = "used for integration tests to inject test versions"
  default     = "goatcommunity/solidblocks-postgres:latest"
}
