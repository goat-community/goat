
##################
## KUBE-HETZNER ##
##################

module "kube-hetzner" {
  providers = {
    hcloud = hcloud
  }
  hcloud_token    = var.hcloud_token
  source          = "kube-hetzner/kube-hetzner/hcloud"
  ssh_public_key  = file(var.kube_hetzner_ssh_public_key)
  ssh_private_key = file(var.kube_hetzner_ssh_private_key)
  network_region  = "eu-central"
  cluster_name    = "dev"
  control_plane_nodepools = [
    {
      name        = "control-plane-nbg1",
      server_type = "cpx11",
      location    = "nbg1",
      labels      = [],
      taints      = [],
      count       = 1
    },
  ]
  agent_nodepools = [
    {
      name        = "agent-large",
      server_type = "cpx31",
      location    = "nbg1",
      labels      = [],
      taints      = [],
      count       = 1
    }
  ]

  load_balancer_type       = "lb11"
  load_balancer_location   = "nbg1"
  ssh_max_auth_tries       = 15
  automatically_upgrade_os = false
  create_kubeconfig        = false
  kured_version            = "1.13.1"
}

output "kubeconfig" {
  value     = module.kube-hetzner.kubeconfig
  sensitive = true
}

#####################################
## POSTGRESQL SRV (DEV && GEONODE) ##
#####################################
resource "hcloud_ssh_key" "db_ssh_key" {
  name       = "postgresql-dev-geonode"
  public_key = file(var.db_ssh_public_key)
}

resource "aws_iam_user" "backup_user" {
  name = "srv_dev_${data.aws_s3_bucket.backup.id}"
}

resource "aws_iam_access_key" "user_keys" {
  user = aws_iam_user.backup_user.name
}

resource "aws_s3_bucket_policy" "backup_bucket_policy" {
  bucket = data.aws_s3_bucket.backup.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "${aws_iam_user.backup_user.arn}"
      },
      "Action": [ "s3:*" ],
      "Resource": [
        "${data.aws_s3_bucket.backup.arn}",
        "${data.aws_s3_bucket.backup.arn}/*"
      ]
    }
  ]
}
EOF
}


resource "random_password" "db_admin_password" {
  length  = 16
  special = false
  numeric = true
  upper   = true
  lower   = true
}

resource "aws_secretsmanager_secret" "db_admin_password" {
  name                    = "dev/DB/AdminPassword"
  description             = "Password for the database admin user"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_admin_password" {
  secret_id     = aws_secretsmanager_secret.db_admin_password.id
  secret_string = random_password.db_admin_password.result
}

data "aws_secretsmanager_secret_version" "db_admin_password" {
  secret_id = aws_secretsmanager_secret.db_admin_password.id

  depends_on = [
    aws_secretsmanager_secret_version.db_admin_password
  ]
}


module "postgresql" {
  source                = "../modules/postgres"
  instance_name         = "geonode-dev-db"
  server_type           = "cpx41"
  docker_shm_size       = "4gb"
  ssh_keys              = [hcloud_ssh_key.db_ssh_key.id]
  data_volume           = data.hcloud_volume.data.id
  backup_s3_bucket      = data.aws_s3_bucket.backup.id
  backup_s3_access_key  = aws_iam_access_key.user_keys.id
  backup_s3_secret_key  = aws_iam_access_key.user_keys.secret
  admin_password        = data.aws_secretsmanager_secret_version.db_admin_password.secret_string
  postgres_extra_config = indent(8, file("./config/postgresql.conf"))
  databases             = []
  network_id            = module.kube-hetzner.network_id
}

output "postgresql_ipv4_address" {
  value = module.postgresql.ipv4_address_private
}
