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
SRC_DIR?=$(CWD)/infra/templates/k8s/deploy


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
AWS:=$(shell which aws) # brew install awscli
HELM:=$(shell which helm) # brew install helm

#=============================
# ===== DEPLOYMENT K8S =======
#=============================

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
	RABBITMQ_DEFAULT_USER=$(RABBITMQ_DEFAULT_USER) \
	RABBITMQ_DEFAULT_PASS=$(RABBITMQ_DEFAULT_PASS) \
	AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
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
	CELERY_RESULT_EXPIRES=$(CELERY_RESULT_EXPIRES) \
	CELERY_TASK_TIME_LIMIT=$(CELERY_TASK_TIME_LIMIT) \
	WORKER_REPLICAS=$(WORKER_REPLICAS) \
	WORKER_MEMORY_LIMIT=$(WORKER_MEMORY_LIMIT) \
	API_REPLICAS=$(API_REPLICAS) \
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
build-client-docker-image: app/client-v2/apps/$(COMPONENT)/Dockerfile
	$(DOCKER) build -f app/client-v2/apps/$(COMPONENT)/Dockerfile --pull -t $(DOCKER_IMAGE) app/client-v2

# target: release-keycloak-theme
release-keycloak-theme: 
	cd app/client-v2/packages/keycloak-theme &&	pnpm install && pnpm run build-keycloak-theme && \
    if [ "$(NAMESPACE)" = "dev" ] || [ "$(NAMESPACE)" = "v2" ]; then \
        mv build_keycloak/target/*.jar p4b-keycloak-theme-dev.jar; \
    else \
        mv build_keycloak/target/*.jar p4b-keycloak-theme.jar; \
    fi && \
	aws s3 cp p4b-keycloak-theme*.jar s3://plan4better-assets/other/keycloak/



# target: make build-docs-docker-image
.PHONY: build-docs-docker-image
build-docs-docker-image: docs/Dockerfile
	$(DOCKER) build -f docs/Dockerfile --pull -t $(DOCKER_IMAGE) docs

# target: make release-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client
.PHONY: release-docker-image
release-docker-image: docker-login build-docker-image
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make release-client-docker-image -e VERSION=some_git_sha_comit -e COMPONENT=api|client|geoserver|print|mapproxy
.PHONY: release-client-docker-image
release-client-docker-image: docker-login build-client-docker-image
	$(DOCKER) push $(DOCKER_IMAGE)

# target: make release-docs-docker-image -e VERSION=some_git_sha_comit
.PHONY: release-docs-docker-image
release-docs-docker-image: docker-login build-docs-docker-image
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
	@echo "Built infra/templates/k8s/deploy/*.yaml from infra/templates/k8s/deploy/*.tpl.yaml"

# target: make deploy -e COMPONENT=api|client
.PHONY: deploy
deploy: setup-kube-config build-k8s
	$(KCTL) apply -f infra/templates/k8s/deploy/$(COMPONENT).yaml

#=============================
# ==== AWS CLOUDFORMATION ====
#=============================

S3_BUCKET?=plan4better-cloud-functions # S3 Bucket to store the cloud formation templates etc.
AWS_DEFAULT_REGION?=eu-central-1
WORKER_TYPE?=goat-heavy-worker

# target: make deploy-worker -e WORKER_TYPE=goat-heavy-worker | goat-superheavy-worker -e NAMESPACE=dev
.PHONY: deploy-worker
deploy-worker:
	@echo "Deploying the cloud formation $(WORKER_TYPE) to AWS"
	aws cloudformation deploy \
	--stack-name $(WORKER_TYPE) \
	--template-file infra/templates/aws/worker-config.yaml \
	--capabilities CAPABILITY_IAM \
	--region $(AWS_DEFAULT_REGION) \
	--s3-bucket $(S3_BUCKET) \
	--s3-prefix goat \
	--no-fail-on-empty-changeset \
	--parameter-overrides workerType=${WORKER_TYPE} \
	--tags app=goat resource=worker

	@echo "Done deploying the $(WORKER_TYPE) to AWS"