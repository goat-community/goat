#!/bin/bash

#https://github.com/multani/action-setup-kustomize/blob/main/setup.sh

set -euo pipefail

VERSION="$1"

# from https://stackoverflow.com/questions/4023830/how-to-compare-two-strings-in-dot-separated-version-format-in-bash
function vercomp() {
  if [[ "$1" == "$2" ]]; then
    return 0
  fi
  local IFS=.
  # shellcheck disable=SC2206
  local i ver1=($1) ver2=($2)
  # fill empty fields in ver1 with zeros
  for ((i = ${#ver1[@]}; i < ${#ver2[@]}; i++)); do
    ver1[i]=0
  done
  for ((i = 0; i < ${#ver1[@]}; i++)); do
    if [[ -z ${ver2[i]} ]]; then
      # fill empty fields in ver2 with zeros
      ver2[i]=0
    fi
    if ((10#${ver1[i]} > 10#${ver2[i]})); then
      return 1
    fi
    if ((10#${ver1[i]} < 10#${ver2[i]})); then
      return 2
    fi
  done
  return 0
}

get_platform() {
  uname | tr '[:upper:]' '[:lower:]'
}

get_arch() {
  local arch; arch=$(uname -m | tr '[:upper:]' '[:lower:]')
  case ${arch} in
  arm64) # m1 macs
    arch='arm64';;
  aarch64) # all other arm64 devices
    arch='arm64';;
  x86_64)
    arch='amd64';;
  *) # fallback
    arch='amd64';;
  esac

  echo "${arch}"
}

get_download_url() {
  local version="$1"
  local platform="$(get_platform)"
  local arch="$(get_arch)"

    vercomp "$version" "3.2.1"
    case $? in
        0) op='=' ;;
        1) op='>' ;;
        2) op='<' ;;
    esac
    if [[ "$op" == '<' ]]; then
        echo "https://github.com/kubernetes-sigs/kustomize/releases/download/v${version}/kustomize_${version}_${platform}_${arch}"
    else
        vercomp "$version" "3.3.0"
        case $? in
            0) op='=' ;;
            1) op='>' ;;
            2) op='<' ;;
        esac
        if [[ "$op" == '<' ]]; then
            echo "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv${version}/kustomize_kustomize.v${version}_${platform}_${arch}"
        else
            echo "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv${version}/kustomize_v${version}_${platform}_${arch}.tar.gz"
        fi
    fi
}


URL="$(get_download_url "$VERSION")"

BIN_DIR="$HOME/.local/bin"
TARGET="$BIN_DIR/kustomize"

mkdir --parents "$BIN_DIR"

set -x

echo "::debug ::Downloading Kustomize from: $URL"

if [[ "$URL" == *"tar.gz"* ]]
then
  TMP_DIR="$(mktemp --directory)"
  curl -sfL -o "$TMP_DIR/kustomize.tgz" "$URL"

  tar xpf "$TMP_DIR/kustomize.tgz" -C "$TMP_DIR"
  cp "$TMP_DIR/kustomize" "$TARGET"
else
  curl -sfL -o "$TARGET" "$URL"
fi

chmod +x "$TARGET"

echo "::debug ::Kustomize ${VERSION} installed in: $TARGET"
sh -xc "$TARGET version"

## Make it available as a regular command
echo "$BIN_DIR" >> "$GITHUB_PATH"