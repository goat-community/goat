export SOLIDBLOCKS_DIR="${SOLIDBLOCKS_DIR:-/solidblocks}"

function bootstrap_package_update {
  apt-get update
}

function bootstrap_package_update_system() {
    apt-get \
        -o Dpkg::Options::="--force-confnew" \
        --force-yes \
        -fuy \
        dist-upgrade
}

function bootstrap_package_check_and_install {
	local package=${1}

	echo -n "checking if package '${package}' is installed..."

	if [[ $(dpkg-query -W -f='${Status}' "${package}" 2>/dev/null | grep -c "ok installed") -eq 0 ]];
	then
		echo "not found, installing now"
		while ! DEBIAN_FRONTEND="noninteractive" apt-get install --no-install-recommends -qq -y "${package}"; do
    		echo "installing failed retrying in 30 seconds"
    		sleep 30
    		apt-get update
		done
	else
		echo "ok"
	fi
}

function bootstrap_solidblocks() {
  bootstrap_package_update
  bootstrap_package_check_and_install "unzip"

  groupadd solidblocks
  useradd solidblocks -g solidblocks

  # shellcheck disable=SC2086
  mkdir -p ${SOLIDBLOCKS_DIR}/{templates,lib,secrets}

  chmod 770 ${SOLIDBLOCKS_DIR}
  chown solidblocks:solidblocks ${SOLIDBLOCKS_DIR}

  chmod -R 770 ${SOLIDBLOCKS_DIR}
  chown -R solidblocks:solidblocks ${SOLIDBLOCKS_DIR}

  chmod -R 700 ${SOLIDBLOCKS_DIR}/secrets

  local temp_file="$(mktemp)"

}