# see https://pellepelster.github.io/solidblocks/cloud-init/storage/#storage_mount
function storage_mount() {

    local storage_device="${1:-}"
    local storage_dir="${2:-}"
    local filesystem="${3:-ext4}"

    while [ ! -b "${storage_device}" ]; do
      echo "waiting for storage device '${storage_device}'"
      sleep 5
    done

    echo "${storage_device} ${storage_dir}   ${filesystem}   defaults  0 0" >> /etc/fstab

    mkdir -p "${storage_dir}"
    mount "${storage_dir}"
}