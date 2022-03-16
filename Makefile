ifneq (,)
This makefile requires GNU Make.
endif

# Project-related variables
SHELL=/bin/bash
NAMESPACE:=dev
DOMAIN:=dev.plan4better.de
PROJECT:=goatcommunity
COMPONENT:=api
VERSION?=$(shell git rev-parse --short HEAD)
REGISTRY?=docker.io
K8S_CLUSTER?=goat
NAMESPACE?=$(shell git rev-parse --abbrev-ref HEAD)
FONTAWESOME_NPM_AUTH_TOKEN?=$(FONTAWESOME_NPM_AUTH_TOKEN)
# Build and test directories
CWD:=$(shell pwd)
SRC_DIR?=$(CWD)/k8s/deploy

ifeq ($(NAMESPACE), main)
	NAMESPACE=prod
	DOMAIN=goat.plan4better.de
endif

ifeq ($(NAMESPACE), staging)
	NAMESPACE=staging
	DOMAIN=goat-test.plan4better.de
endif

ifeq ($(NAMESPACE), dev)
	NAMESPACE=dev
	DOMAIN=goat-dev.plan4better.de
endif

DOCKER_IMAGE?=$(REGISTRY)/$(PROJECT)/$(COMPONENT)_${NAMESPACE}:$(VERSION)

# Build and test tools abstraction
DOCKER:=$(shell which docker) # https://docs.docker.com/docker-for-mac/install/
KCTL:=$(shell which kubectl) # brew install kubernetes-cli
HELM:=$(shell which helm) # brew install helm

# Templating magic
K8S_SRC:=$(wildcard $(SRC_DIR)/*.tpl.yaml)
K8S_OBJ:=$(patsubst %.tpl.yaml,%.yaml,$(K8S_SRC))

%.yaml: %.tpl.yaml
	DOCKER_IMAGE=$(DOCKER_IMAGE) \
	NAMESPACE=$(NAMESPACE) \
	DOMAIN=$(DOMAIN) \
	VERSION=$(VERSION) \
	POSTGRES_HOST=$(POSTGRES_HOST) \
	POSTGRES_DB=$(POSTGRES_DB) \
	POSTGRES_USER=$(POSTGRES_USER) \
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	API_SECRET_KEY=$(API_SECRET_KEY) \
	SENTRY_DSN=$(SENTRY_DSN) \
	FONTAWESOME_NPM_AUTH_TOKEN=$(FONTAWESOME_NPM_AUTH_TOKEN) \
	t=$$(cat $<); eval "echo \"$${t}\"" > $@

# target: make help - displays this help.
.PHONY: help
help:
	@egrep '^# target' [Mm]akefile

# target: make setup-general-utils
.PHONY: setup-general-utils
setup-general-utils:
	$(KCTL) config use-context $(K8S_CLUSTER)
	$(KCTL) apply -f k8s/deploy/general.yaml

# target: make setup-kube-config
.PHONY: setup-kube-config
setup-kube-config:
	mkdir -p ${HOME}/.kube/
	cp k8s/deploy/config ${HOME}/.kube/config
	$(KCTL) config set "clusters.goat.server" "${KUBE_CLUSTER_SERVER}"
	$(KCTL) config set "clusters.goat.certificate-authority-data" "${KUBE_CLUSTER_CERTIFICATE}"
	$(KCTL) config set "users.goat-admin.token" "${KUBE_CLIENT_TOKEN}"

# target: make setup-alb-ingress
# .PHONY: setup-alb-ingress
# setup-alb-ingress: setup-general-utils
# 	$(KCTL) apply -f k8s/utils/alb-ingress.yaml

# target: make docker-login
.PHONY: docker-login
docker-login:
	$(DOCKER) login -u $(DOCKER_USERNAME) -p $(DOCKER_PASSWORD) $(REGISTRY)

# target: make build-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: build-docker-image
build-docker-image: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/$(COMPONENT)

# target: build-client-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: build-client-docker-image
build-client-docker-image: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/$(COMPONENT) --build-arg FONTAWESOME_NPM_AUTH_TOKEN=$(FONTAWESOME_NPM_AUTH_TOKEN)


# target: make release-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: release-docker-image
release-docker-image: docker-login build-docker-image
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make release-client-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: release-client-docker-image
release-client-docker-image: docker-login build-client-docker-image
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make after-success
.PHONY: after-success
after-success:
	@echo "Hooray! :)"

# target: make build-k8s -e VERSION=some_git_sha_comit
.PHONY: build-k8s
build-k8s:
	rm -f $(K8S_OBJ)
	make $(K8S_OBJ)
	@echo "Built k8s/deploy/*.yaml from k8s/*.tpl.yaml"

# target: make deploy -e COMPONENT=api|client
.PHONY: deploy
deploy: setup-kube-config build-k8s
	$(KCTL) config use-context goat && $(KCTL) apply -f k8s/deploy/$(COMPONENT).yaml
