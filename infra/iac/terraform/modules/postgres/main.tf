locals {

  user_data = templatefile("${path.module}/user_data.sh", {
    db_instance_name      = var.instance_name
    postgres_docker_image = var.postgres_docker_image
    docker_shm_size       = var.docker_shm_size
    storage_device_data   = data.hcloud_volume.data.linux_device
    storage_device_backup = try(data.hcloud_volume.backup[0].linux_device, "")
    cloud_init_bootstrap  = file("${path.module}/../../scripts/db/cloud_init_bootstrap.sh")
    cloud_init_storage    = file("${path.module}/../../scripts/db/lib/storage.sh")
    cloud_init_lego       = file("${path.module}/../../scripts/db/lib/lego.sh")
    backup_full_calendar  = var.backup_full_calendar
    backup_incr_calendar  = var.backup_incr_calendar

    db_admin_password            = var.admin_password == null ? "" : var.admin_password
    db_backup_s3_bucket          = var.backup_s3_bucket == null ? "" : var.backup_s3_bucket
    db_backup_s3_access_key      = var.backup_s3_access_key == null ? "" : var.backup_s3_access_key
    db_backup_s3_secret_key      = var.backup_s3_secret_key == null ? "" : var.backup_s3_secret_key
    db_backup_s3_retention_full  = var.backup_s3_retention_full == null ? "" : var.backup_s3_retention_full
    db_backup_s3_retention_diff  = var.backup_s3_retention_diff == null ? "" : var.backup_s3_retention_diff
    db_postgres_extra_config     = var.postgres_extra_config == null ? "" : var.postgres_extra_config
    backup_encryption_passphrase = var.backup_encryption_passphrase == null ? "" : var.backup_encryption_passphrase
    mode                         = var.mode == null ? "" : var.mode

    databases = var.databases

    ssl_enable              = var.ssl_enable
    ssl_email               = var.ssl_email
    ssl_domains             = var.ssl_domains
    ssl_dns_provider        = var.ssl_dns_provider
    ssl_dns_provider_config = var.ssl_dns_provider_config

    pre_script  = var.pre_script
    post_script = var.post_script
  })
}

# Render to local file on machine (for debugging purposes. !!! DO NOT COMMIT !!!)
# resource "local_file" "user_data_rendered" {
#   content  = local.user_data
#   filename = "${path.module}/user_data_rendered.sh"
# }

resource "hcloud_server" "instance" {
  name        = var.instance_name
  server_type = var.server_type
  image       = var.server_image
  location    = var.location
  ssh_keys    = var.ssh_keys
  user_data   = local.user_data

  public_net {
    ipv4_enabled = var.public_net_ipv4_enabled
    ipv6_enabled = var.public_net_ipv6_enabled
  }

  dynamic "network" {
    for_each = var.network_id != null ? toset([
      { network_id : var.network_id, network_ip : var.network_ip }
    ]) : toset([])

    content {
      network_id = network.value.network_id
      ip         = network.value.network_ip
    }
  }

  labels = var.labels
}


resource "hcloud_volume_attachment" "data" {
  server_id = hcloud_server.instance.id
  volume_id = var.data_volume
}

resource "hcloud_volume_attachment" "backup" {
  count     = var.backup_volume > 0 ? 1 : 0
  server_id = hcloud_server.instance.id
  volume_id = var.backup_volume
}
