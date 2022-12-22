ifneq (,)
This makefile requires GNU Make.
endif

# Project-related variables
SHELL=/bin/bash
DOMAIN:=dev.plan4better.de
PROJECT:=goatcommunity
COMPONENT:=api
VERSION?=$(shell git rev-parse --short HEAD)
REGISTRY?=docker.io
K8S_CLUSTER?=goat
NAMESPACE?=$(shell git rev-parse --abbrev-ref HEAD)
# Build and test directories
CWD:=$(shell pwd)
SRC_DIR?=$(CWD)/k8s/deploy

ifeq ($(NAMESPACE), prod)
	DOMAIN=goat.plan4better.de
endif

ifeq ($(NAMESPACE), staging)
	DOMAIN=goat-test.plan4better.de
endif

ifeq ($(NAMESPACE), dev)
	DOMAIN=goat-dev.plan4better.de
endif

DOCKER_IMAGE?=$(REGISTRY)/$(PROJECT)/$(COMPONENT)-${NAMESPACE}:$(VERSION)

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
	R5_HOST=$(R5_HOST) \
	R5_AUTHORIZATION=$(R5_AUTHORIZATION) \
	POSTGRES_DB=$(POSTGRES_DB) \
	POSTGRES_USER=$(POSTGRES_USER) \
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	API_SECRET_KEY=$(API_SECRET_KEY) \
	SENTRY_DSN=$(SENTRY_DSN) \
	EMAILS_FROM_EMAIL=$(EMAILS_FROM_EMAIL) \
	FIRST_SUPERUSER_EMAIL=$(FIRST_SUPERUSER_EMAIL) \
	FIRST_SUPERUSER_PASSWORD=$(FIRST_SUPERUSER_PASSWORD) \
	FIRST_ORGANIZATION=$(FIRST_ORGANIZATION) \
    FIRST_SUPERUSER_NAME=$(FIRST_SUPERUSER_NAME) \
    FIRST_SUPERUSER_SURNAME=$(FIRST_SUPERUSER_SURNAME) \
	SMTP_PASSWORD=$(SMTP_PASSWORD) \
	t=$$(cat $<); eval "echo \"$${t}\"" > $@

# target: make help - displays this help.
.PHONY: help
help:
	@egrep '^# target' [Mm]akefile

#  target: make setup-kube-config
.PHONY: setup-kube-config
setup-kube-config:
	mkdir -p ${HOME}/.kube/
	@echo ${KUBE_CONFIG} | base64 -d > ${HOME}/.kube/config

# target: make docker-login
.PHONY: docker-login
docker-login:
	$(DOCKER) login -u $(DOCKER_USERNAME) -p $(DOCKER_PASSWORD) $(REGISTRY)

# make docker-build for pr workflow (without tag)
# target: make build-docker-image-pr -e COMPONENT=api|client
.PHONY: build-docker-image-pr
build-docker-image-pr: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile app/$(COMPONENT) --build-arg FONTAWESOME_NPM_AUTH_TOKEN=$(FONTAWESOME_NPM_AUTH_TOKEN)

# target: make build-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client
.PHONY: build-docker-image
build-docker-image: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/$(COMPONENT)

# target: build-client-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client
.PHONY: build-client-docker-image
build-client-docker-image: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/$(COMPONENT) --build-arg FONTAWESOME_NPM_AUTH_TOKEN=$(FONTAWESOME_NPM_AUTH_TOKEN)


# target: make release-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client
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
	@echo "Built k8s/deploy/*.yaml from k8s/deploy/*.tpl.yaml"

# target: make deploy -e COMPONENT=api|client
.PHONY: deploy
deploy: setup-kube-config build-k8s
	$(KCTL) apply -f k8s/deploy/$(COMPONENT).yaml

# target: make deploy-service -e COMPONENT=api|client
.PHONY: deploy-service
deploy-service: setup-kube-config build-k8s
	$(KCTL) replace -f k8s/deploy/$(COMPONENT).yaml