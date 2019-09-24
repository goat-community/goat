#!/usr/bin/env bash

DOCKER_ENV=''
DOCKER_TAG=''

case "$TRAVIS_BRANCH" in
  "master")
    DOCKER_ENV=production
    DOCKER_TAG=latest
    ;;
  "test_travis")
    DOCKER_ENV=development
    DOCKER_TAG=test
    ;;
  "development")
  DOCKER_ENV=development
  DOCKER_TAG=dev
  ;;
esac

docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD

docker build -f app/client/Dockerfile -t goat-client:$DOCKER_TAG app/client --no-cache
docker build -f app/api/Dockerfile -t goat-api:$DOCKER_TAG app/api --no-cache
docker build -f app/print/Dockerfile -t goat-print:$DOCKER_TAG app/print --no-cache

docker tag goat-client:$DOCKER_TAG $DOCKER_USERNAME/goat-client:$DOCKER_TAG
docker tag goat-api:$DOCKER_TAG $DOCKER_USERNAME/goat-api:$DOCKER_TAG
docker tag goat-print:$DOCKER_TAG $DOCKER_USERNAME/goat-print:$DOCKER_TAG

docker push $DOCKER_USERNAME/goat-client:$DOCKER_TAG
docker push $DOCKER_USERNAME/goat-api:$DOCKER_TAG
docker push $DOCKER_USERNAME/goat-print:$DOCKER_TAG
