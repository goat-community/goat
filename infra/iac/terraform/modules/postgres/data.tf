data "hcloud_volume" "data" {
  id = var.data_volume
}

data "hcloud_volume" "backup" {
  count = var.backup_volume > 0 ? 1 : 0
  id    = var.backup_volume
}
