ifneq (,)
This makefile requires GNU Make.
endif

ifeq ($(TRAVIS_BRANCH), master)
	NAMESPACE=production
endif

# Project-related variables
SHELL=/bin/bash
NAMESPACE:=development
PROJECT:=goatcommunity
COMPONENT:=api
VERSION?=$(shell git rev-parse HEAD)
REGISTRY?=docker.io
DOCKER_IMAGE?=$(REGISTRY)/$(PROJECT)/$(COMPONENT):$(VERSION)
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
	NAMESPACE=$(NAMESPACE) \
	VERSION=$(VERSION) \
	POSTGRES_DB=$(POSTGRES_DB) \
	POSTGRES_USER=$(POSTGRES_USER) \
	POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
	t=$$(cat $<); eval "echo \"$${t}\"" > $@

# target: make help - displays this help.
.PHONY: help
help:
	@egrep '^# target' [Mm]akefile

# target: make setup-kube-config
.PHONY: setup-kube-config
setup-kube-config:
	mkdir -p ${HOME}/.kube/
	cp k8s/config ${HOME}/.kube/config
	$(KCTL) config set "clusters.goat.server" "${KUBE_CLUSTER_SERVER}"
	$(KCTL) config set "clusters.goat.certificate-authority-data" "${KUBE_CLUSTER_CERTIFICATE}"
	$(KCTL) config set "users.goat-admin.token" "${KUBE_CLIENT_TOKEN}"

# target: make docker-login
.PHONY: docker-login
docker-login:
	$(DOCKER) login -u $(DOCKER_USERNAME) -p $(DOCKER_PASSWORD) $(REGISTRY)

# target: make build-docker-image VERSION=some_git_sha_comit COMPONENT=api|client
.PHONY: build-docker-image
build-docker-image: app/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/$(COMPONENT)

# target: make release-docker-image VERSION=some_git_sha_comit
.PHONY: release-docker-image
release-docker-image: docker-login build-docker-image
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make after-success
.PHONY: after-success
after-success:
	@echo "Hooray! :)"

# target: make build-k8s VERSION=some_git_sha_comit
.PHONY: build-k8s
build-k8s:
	rm -f $(K8S_OBJ)
	make $(K8S_OBJ)
	@echo "Built k8s/*.yaml from k8s/*.tpl.yaml"

# target: make deploy-postgres-server
.PHONY: deploy-postgres-server
deploy-postgres-server: setup-kube-config build-k8s
	$(KCTL) config use-context goat && $(KCTL) apply -f k8s/postgres.yaml
