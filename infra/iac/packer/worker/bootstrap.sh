#!/usr/bin/env bash

set -e

sudo apt-get -y update

# INSTALL DEPS(docker,npm,git) 
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
sh /tmp/get-docker.sh
sudo apt-get install -y npm git


