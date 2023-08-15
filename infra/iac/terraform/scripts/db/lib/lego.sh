function go_arch() {
  case $(uname -m) in
    armv7l) echo "armv7" ;;
    aarch64) echo "arm64" ;;
    x86_64) echo "amd64" ;;
    *) echo "unknown" ;;
  esac
}

function lego_certificate_renewal {
  local base_lego_command="${1}"
  local run_hook="${2}"

cat <<-EOF
[Unit]
Description=renew ssl certificates

[Service]
Type=oneshot
EnvironmentFile=${SOLIDBLOCKS_DIR}/secrets/lego.env
ExecStart=${base_lego_command} renew --run-hook="${run_hook}"
EOF
}

function lego_certificate_renewal_timer {
cat <<-EOF
[Unit]
Description=renew ssl certificates timer

[Timer]
Persistent=true
OnCalendar=*-*-* 3:35
RandomizedDelaySec=1h

Unit=lego-certificate-renewal.service

[Install]
WantedBy=multi-user.target
EOF
}


# see https://pellepelster.github.io/solidblocks/cloud-init/lego/#lego_setup_dns
function lego_setup_dns() {
  local lego_path="${1}"
  local lego_email="${2}"
  local lego_domains="${3}"
  local lego_dns_provider="${4}"
  local run_hook="${5:-/bin/true}"
  local lego_server="${6:-https://acme-v02.api.letsencrypt.org/directory}"

  shift || true
  shift || true
  shift || true
  shift || true

  local temp_dir="/tmp/lego_setup_$$"
  mkdir -p "${temp_dir}"

  (
    LEGO_VERSION="4.12.3"

    declare -A LEGO_CHECKSUMS
    LEGO_CHECKSUMS[amd64]="222ec9e8ac676d79161465521268eebb7a9c6da4f79e0b53a1b9a8937f8dd75c"
    LEGO_CHECKSUMS[armv7]="ca90c55f0886b3a7f64f67f7c1f9477d710f86376c797501b438ab6d382c887c"
    LEGO_CHECKSUMS[arm64]="61453f3990e0475b99266559abca39943ae66569b3980a2437ebf35bd17376a3"

    cd "${temp_dir}"
    curl -L "https://github.com/go-acme/lego/releases/download/v${LEGO_VERSION}/lego_v${LEGO_VERSION}_linux_$(go_arch).tar.gz" -o "lego_v${LEGO_VERSION}_linux_$(go_arch).tar.gz"
    echo "${LEGO_CHECKSUMS[$(go_arch)]}  lego_v${LEGO_VERSION}_linux_$(go_arch).tar.gz" | sha256sum -c
    tar -xzvf lego_v${LEGO_VERSION}_linux_$(go_arch).tar.gz
    mv lego /usr/bin/lego
    chmod +x /usr/bin/lego
  )

  rm -rf "${temp_dir}"
  mkdir -p "${lego_path}"

  local domain_args=""
  for domain in ${lego_domains}; do
    domain_args="${domain_args} --domains ${domain}"
  done

  # preserve DNS provider specific env variables
  echo "" > "${SOLIDBLOCKS_DIR}/secrets/lego.env"
  for var in $(lego dnshelp -c ${lego_dns_provider} | sed -nr 's/^\s*\-\s*"(.*)"\s*:.*$/\1/p'); do
    if env | grep "${var}"; then
      echo "${var}=${!var}" >> "${SOLIDBLOCKS_DIR}/secrets/lego.env"
    fi
  done

  local base_lego_command="/usr/bin/lego --accept-tos --server="${lego_server}" --email "${lego_email}" --dns "${lego_dns_provider}" ${domain_args} --path "${lego_path}""

  ${base_lego_command} run --run-hook="${run_hook}"

  lego_certificate_renewal_timer > /etc/systemd/system/lego-certificate-renewal.timer
  lego_certificate_renewal "${base_lego_command}" "${run_hook}" > /etc/systemd/system/lego-certificate-renewal.service

  systemctl daemon-reload

  systemctl enable lego-certificate-renewal
  systemctl enable lego-certificate-renewal.timer
}