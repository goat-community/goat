data "aws_s3_bucket" "backup" {
  bucket = var.s3_backup_bucket
}

data "hcloud_volume" "data" {
  name = var.hcloud_postgresql_data_volume
}
