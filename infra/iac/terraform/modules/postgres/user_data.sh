#!/usr/bin/env bash

set -eu -o pipefail

# start of pre_script
${pre_script}
# end of pre_script

STORAGE_DEVICE_DATA="${storage_device_data}"

# ssl config
SSL_ENABLE="${ssl_enable}"
SSL_EMAIL="${ssl_email}"
SSL_DNS_PROVIDER="${ssl_dns_provider}"

SSL_DOMAINS=""
%{ for domain in ssl_domains }
SSL_DOMAINS="$${SSL_DOMAINS} ${domain}"
%{ endfor }

# ssl dns provider config
%{ for key, value in ssl_dns_provider_config }
export ${key}="${value}"
%{ endfor }

%{~ if storage_device_backup != "" ~}
STORAGE_DEVICE_BACKUP="${storage_device_backup}"
%{~ endif ~}

${cloud_init_bootstrap}

${cloud_init_storage}

${cloud_init_lego}

bootstrap_solidblocks

function install_prerequisites {
  apt-get install --no-install-recommends -qq -y \
    apparmor \
    docker.io \
    docker-compose \
    ufw \
    uuid \
    unattended-upgrades
}

function configure_ufw {
  ufw enable
  ufw allow ssh
  ufw allow 5432
}

function rds_service_systemd_backup_config {
local backup_type="$${1:-}"
cat <<-EOF
[Unit]
Description=full backup for %i

[Service]
Type=oneshot
WorkingDirectory=/opt/dockerfiles/%i
ExecStart=/usr/bin/docker-compose exec -T ${db_instance_name} /rds/bin/backup-$${backup_type}.sh
EOF
}

function rds_service_systemd_backup_timer {
local backup_type="$${1:-}"
local backup_calendar="$${2:-}"
cat <<-EOF
[Unit]
Description=full backup for %i

[Timer]
OnCalendar=$${backup_calendar}

Unit=rds-backup-$${backup_type}@%i.service

[Install]
WantedBy=multi-user.target
EOF
}

function rds_service_systemd_config {
cat <<-EOF
[Unit]
Description=rds instance %i
Requires=docker.service
After=docker.service

[Service]
Restart=always
RestartSec=10s

WorkingDirectory=/opt/dockerfiles/%i
ExecStartPre=/usr/bin/docker-compose down -v
ExecStartPre=/usr/bin/docker-compose rm -fv
ExecStartPre=/usr/bin/docker-compose pull

# Compose up
ExecStart=/usr/bin/docker-compose up

# Compose down, remove containers and volumes
ExecStop=/usr/bin/docker-compose down -v

[Install]
WantedBy=multi-user.target
EOF
}

function lego_run_hook_script {
cat <<-EOF
#!/usr/bin/env bash

set -eu

chown rds:rds "\$${LEGO_CERT_PATH}"
chmod 600 "\$${LEGO_CERT_PATH}"

chown rds:rds "\$${LEGO_CERT_KEY_PATH}"
chmod 600 "\$${LEGO_CERT_KEY_PATH}"
EOF
}

function docker_compose_config {
cat <<-EOF
version: "3"
services:
  ${db_instance_name}:
    image: ${postgres_docker_image}
    container_name: ${db_instance_name}_postgresql
    %{~ if mode != "" ~}
    command: ${mode}
    %{~ endif ~}
    environment:
      DB_INSTANCE_NAME: ${db_instance_name}
      %{~ if db_admin_password != "" ~}
      DB_ADMIN_PASSWORD: ${db_admin_password}
      %{~ endif ~}
      %{~ for database in databases ~}
      DB_DATABASE_${database.id}: ${database.id}
      DB_USERNAME_${database.id}: ${database.user}
      DB_PASSWORD_${database.id}: ${database.password}
      %{~ endfor ~}
      %{~ if db_backup_s3_bucket != "" && db_backup_s3_access_key != "" && db_backup_s3_secret_key != "" ~}
      DB_BACKUP_S3: 1
      DB_BACKUP_S3_BUCKET: ${db_backup_s3_bucket}
      DB_BACKUP_S3_ACCESS_KEY: ${db_backup_s3_access_key}
      DB_BACKUP_S3_SECRET_KEY: ${db_backup_s3_secret_key}
      %{~ endif ~}
      %{~ if db_backup_s3_retention_full != "" ~}
      DB_BACKUP_S3_RETENTION_FULL: ${db_backup_s3_retention_full}
      %{~ endif ~}
      %{~ if db_backup_s3_retention_diff != "" ~}
      DB_BACKUP_S3_RETENTION_DIFF: ${db_backup_s3_retention_diff}
      %{~ endif ~}
      %{~ if storage_device_backup != "" ~}
      DB_BACKUP_LOCAL: 1
      %{~ endif ~}
      %{~ if backup_encryption_passphrase != "" ~}
      DB_BACKUP_ENCRYPTION_PASSPHRASE: ${backup_encryption_passphrase}
      %{~ endif ~}
      %{~ if db_postgres_extra_config != "" ~}
      DB_POSTGRES_EXTRA_CONFIG: |
      
        ${db_postgres_extra_config}
      %{~ endif ~}

    ports:
      - "5432:5432"
    volumes:
      - "/storage/data:/storage/data"
      %{~ if storage_device_backup != "" ~}
      - "/storage/backup:/storage/backup"
      %{~ endif ~}
      %{~ if ssl_enable ~}
      - "/storage/data/ssl/certificates/${ssl_domains[0]}.crt:/rds/ssl/server.crt"
      - "/storage/data/ssl/certificates/${ssl_domains[0]}.key:/rds/ssl/server.key"
      %{~ endif ~}
EOF
}



groupadd --gid 10000 rds
useradd --gid rds --uid 10000 rds --create-home

storage_mount "$${STORAGE_DEVICE_DATA}" "/storage/data"

%{~ if storage_device_backup != "" ~}
storage_mount "$${STORAGE_DEVICE_BACKUP}" "/storage/backup"
%{~ endif ~}

chown -R rds:rds "/storage"

install_prerequisites
configure_ufw

if [[ "$${SSL_ENABLE}" == "true" ]]; then
  lego_run_hook_script > ~rds/lego_run_hook.sh
  chmod +x ~rds/lego_run_hook.sh
  lego_setup_dns "/storage/data/ssl" "$${SSL_EMAIL}" "$${SSL_DOMAINS}" "$${SSL_DNS_PROVIDER}" "$(readlink -f ~rds/lego_run_hook.sh)" "https://acme-staging-v02.api.letsencrypt.org/directory"
fi

mkdir -p "/opt/dockerfiles/${db_instance_name}"
docker_compose_config > "/opt/dockerfiles/${db_instance_name}/docker-compose.yml"

rds_service_systemd_config > /etc/systemd/system/rds@.service
rds_service_systemd_backup_config "full" > /etc/systemd/system/rds-backup-full@.service
rds_service_systemd_backup_timer "full" "${backup_full_calendar}" > /etc/systemd/system/rds-backup-full@.timer

rds_service_systemd_backup_config "incr" > /etc/systemd/system/rds-backup-incr@.service
rds_service_systemd_backup_timer "incr" "${backup_incr_calendar}" > /etc/systemd/system/rds-backup-incr@.timer

systemctl daemon-reload

systemctl enable rds@${db_instance_name}
systemctl start rds@${db_instance_name}

systemctl enable rds-backup-full@${db_instance_name}.timer
systemctl enable rds-backup-incr@${db_instance_name}.timer

# enable automatic system updates
systemctl start unattended-upgrades
systemctl enable unattended-upgrades

# start of post_script
${post_script}
# end of post_script