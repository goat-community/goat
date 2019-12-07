ifneq (,)
This makefile requires GNU Make.
endif

# Project-related variables
NAMESPACE:=production
PROJECT:=goat
POSTGRES_SRVC:=some_postgres_FDQN
COMPONENT:=api
VERSION?=$(shell git rev-parse HEAD)
REGISTRY?=goatcommunity
DOCKER_IMAGE?=$(REGISTRY)/$(PROJECT)-$(COMPONENT):$(VERSION)
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
	POSTGRES_SRVC=$(POSTGRES_SRVC) \
	VERSION=$(VERSION) \
	t=$$(cat $<); eval "echo \"$${t}\"" > $@

# target: make help - displays this help.
.PHONY: help
help:
	@egrep '^# target' [Mm]akefile
