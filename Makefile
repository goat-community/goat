ifneq (,)
This makefile requires GNU Make.
endif

ifeq ($(TRAVIS_BRANCH), master)
	NAMESPACE=production
endif

# Project-related variables
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
	t=$$(cat $<); eval "echo \"$${t}\"" > $@

# target: make help - displays this help.
.PHONY: help
help:
	@egrep '^# target' [Mm]akefile

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
