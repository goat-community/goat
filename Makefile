ifneq (,)
This makefile requires GNU Make.
endif

ifeq ($(TRAVIS_BRANCH), master)
	NAMESPACE=production
endif

# Project-related variables
SHELL=/bin/bash
NAMESPACE:=development
DOMAIN:=demo.open-accessibility.org
PROJECT:=goatcommunity
COMPONENT:=api
VERSION?=$(shell git rev-parse HEAD)
REGISTRY?=docker.io
DOCKER_IMAGE?=$(REGISTRY)/$(PROJECT)/$(COMPONENT):$(VERSION)
POSTGIS_DOCKER_IMAGE?=$(REGISTRY)/$(PROJECT)/db:$(VERSION)
K8S_CLUSTER?=goat

# Build and test directories
CWD:=$(shell pwd)
SRC_DIR?=$(CWD)/k8s

# Build and test tools abstraction
DOCKER:=$(shell which docker) # https://docs.docker.com/docker-for-mac/install/
KCTL:=$(shell which kubectl) # brew install kubernetes-cli
HELM:=$(shell which helm) # brew install helm

# Templating magic
K8S_SRC:=$(wildcard $(SRC_DIR)/*.tpl.yaml)
K8S_OBJ:=$(patsubst %.tpl.yaml,%.yaml,$(K8S_SRC))

%.yaml: %.tpl.yaml
	DOCKER_IMAGE=$(DOCKER_IMAGE) \
	POSTGIS_DOCKER_IMAGE=$(POSTGIS_DOCKER_IMAGE) \
	NAMESPACE=$(NAMESPACE) \
	DOMAIN=$(DOMAIN) \
	VERSION=$(VERSION) \
	POSTGRES_DB=$(POSTGRES_DB) \
	POSTGRES_USER=$(POSTGRES_USER) \
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	t=$$(cat $<); eval "echo \"$${t}\"" > $@

# target: make help - displays this help.
.PHONY: help
help:
	@egrep '^# target' [Mm]akefile

# target: make setup-general-utils
.PHONY: setup-general-utils
setup-general-utils:
	$(KCTL) config use-context $(K8S_CLUSTER)
	$(KCTL) apply -f k8s/general.yaml

# target: make setup-kube-config
.PHONY: setup-kube-config
setup-kube-config:
	mkdir -p ${HOME}/.kube/
	cp k8s/config ${HOME}/.kube/config
	$(KCTL) config set "clusters.goat.server" "${KUBE_CLUSTER_SERVER}"
	$(KCTL) config set "clusters.goat.certificate-authority-data" "${KUBE_CLUSTER_CERTIFICATE}"
	$(KCTL) config set "users.goat-admin.token" "${KUBE_CLIENT_TOKEN}"

# target: make setup-nginx
.PHONY: setup-nginx
setup-nginx: setup-general-utils
	$(HELM) -n default install nginx-ingress stable/nginx-ingress --set controller.publishService.enabled=true
	$(KCTL) -n cert-manager apply -f https://raw.githubusercontent.com/jetstack/cert-manager/release-0.11/deploy/manifests/00-crds.yaml
	$(HELM) repo add jetstack https://charts.jetstack.io
	$(HELM) install cert-manager --namespace cert-manager jetstack/cert-manager
	$(KCTL) apply -f k8s/letscrypt.yaml

# target: make docker-login
.PHONY: docker-login
docker-login:
	$(DOCKER) login -u $(DOCKER_USERNAME) -p $(DOCKER_PASSWORD) $(REGISTRY)

# target: make build-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: build-docker-image
build-docker-image: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/$(COMPONENT)

# target: make release-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: release-docker-image
release-docker-image: docker-login build-docker-image
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make build-docker-image-app-context -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: build-docker-image-app-context
build-docker-image-app-context: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app

# target: make release-docker-image-app-context -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: release-docker-image-app-context
release-docker-image-app-context: docker-login build-docker-image-app-context
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make build-database-docker-image -e VERSION=some_git_sha_comit
.PHONY: build-database-docker-image
build-database-docker-image: app/database/Dockerfile
	$(DOCKER) build -f app/database/Dockerfile --pull -t $(POSTGIS_DOCKER_IMAGE) app

# target: make release-database-docker-image -e VERSION=some_git_sha_comit
.PHONY: release-database-docker-image
release-database-docker-image: docker-login build-database-docker-image
	$(DOCKER) push $(POSTGIS_DOCKER_IMAGE)

# target: make after-success
.PHONY: after-success
after-success:
	@echo "Hooray! :)"

# target: make build-k8s -e VERSION=some_git_sha_comit
.PHONY: build-k8s
build-k8s:
	rm -f $(K8S_OBJ)
	make $(K8S_OBJ)
	@echo "Built k8s/*.yaml from k8s/*.tpl.yaml"

# target: make deploy-postgres-server
.PHONY: deploy-postgres-server
deploy-postgres-server: setup-kube-config build-k8s
	$(KCTL) config use-context goat && $(KCTL) apply -f k8s/postgres.yaml

# target: make deploy -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: deploy
deploy: setup-kube-config build-k8s
	$(KCTL) config use-context goat && $(KCTL) apply -f k8s/$(COMPONENT).yaml
