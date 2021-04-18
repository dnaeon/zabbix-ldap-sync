SHELL = bash
IMAGE_REPO = scoopex666
IMAGE_NAME = zabbix-ldap-sync
TAG = dev
TAG_PUBLISH = $(shell git describe --abbrev=0 --tags)_$(shell date --date="today" "+%Y-%m-%d_%H-%M-%S")
FORCE_UPGRADE_MARKER ?= $(shell date "+%Y-%m-%d")

.PHONY: all deps clean prune

venv = . venv/bin/activate

## public

all: deps

deps: venv/bin/activate

venv/bin/activate: Makefile
	@which python3 > /dev/null || { echo "Missing requirement: python3" >&2; exit 1; }
	virtualenv --version > /dev/null || { echo "Missing requirement: virtualenv -- aborting" >&2; exit 1; }
	[ -e venv/bin/python ] || virtualenv -p $$(which python3) venv > /dev/null
	${venv} && pip3 install -r requirements.txt
	touch venv/bin/activate

clean:
	rm -rf __pycache__

prune: clean
	rm -rf venv

test: deps
	${venv} && PYTHONPATH=zabbix-ldap-sync pytest

check: lint type-check
.PHONY: check

lint: deps
	${venv} && python3 -m flake8 zabbix-ldap-sync lib
.PHONY: lint

type-check: deps
	${venv} && python3 -m mypy zabbix-ldap-sync lib
.PHONY: lint


build:
	docker build -t ${IMAGE_NAME}:${TAG} --build-arg FORCE_UPGRADE_MARKER="${FORCE_UPGRADE_MARKER}" -f Dockerfile .
	@docker images ${IMAGE_NAME}:${TAG} --format='DockerImage Size: {{.Size}}'

clean_docker:
	docker rmi ${IMAGE_NAME}:${TAG} || true

publish: clean_docker build
	docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_REPO}/${IMAGE_NAME}:${TAG_PUBLISH}
	docker push ${IMAGE_REPO}/${IMAGE_NAME}:${TAG_PUBLISH}
	docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_REPO}/${IMAGE_NAME}:latest
	docker push ${IMAGE_REPO}/${IMAGE_NAME}:latest

testdocker: build
   docker run --rm --name ${IMAGE_NAME} ${IMAGE_NAME}:${TAG} -- -c zabbix-ldap.conf.example

inspect: build
   docker run --rm --name ${IMAGE_NAME} -ti  ${IMAGE_NAME}:${TAG} -- bash

