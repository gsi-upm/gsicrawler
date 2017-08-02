NAME=gsicrawler

DEVPORT=8080


# Deployment with Kubernetes
# 

# Check if the KUBE_CA_PEM_FILE exists. Otherwise, create it from KUBE_CA_BUNDLE
KUBE_CA_TEMP=false
ifeq ($(wildcard $(KUBE_CA_PEM_FILE)),) 
    KUBE_CA_PEM_FILE:=$(shell mktemp)
	CREATED:=$(shell echo -e "$$KUBE_CA_BUNDLE" > $(KUBE_CA_PEM_FILE))
	KUBE_CA_TEMP=true
else
	KUBE_CA_PEM_FILE=""
endif 
KUBE_URL=""
KUBE_TOKEN=""
KUBE_NAMESPACE=$(NAME)
KUBECTL=docker run --rm -v $(KUBE_CA_PEM_FILE):/tmp/ca.pem -v $$PWD:/tmp/cwd/ -i lachlanevenson/k8s-kubectl --server="$(KUBE_URL)" --token="$(KUBE_TOKEN)" --certificate-authority="/tmp/ca.pem" -n $(KUBE_NAMESPACE)

CI_PROJECT_NAME=$(NAME)
CI_REGISTRY=docker.io
CI_REGISTRY_USER=gitlab
CI_COMMIT_REF_NAME=master
LUIGI_IMAGE=registry.cluster.gsi.dit.upm.es/sefarad/gsicrawler/luigi
WEB_IMAGE=registry.cluster.gsi.dit.upm.es/sefarad/gsicrawler/web

info:
	@echo $(KUBE_CA_PEM_FILE)
	@echo $(KUBE_CA_TEMP)
	cat $(KUBE_CA_PEM_FILE)
	@echo $$KUBE_CA_BUNDLE
	@echo $(CREATED)

deploy:
	@$(KUBECTL) apply -f /tmp/cwd/k8s/

deploy-check:
	@$(KUBECTL) get deploy,pods,svc,ingress

login:
ifeq ($(CI_BUILD_TOKEN),)
	@echo "Not logging to the docker registry" "$(CI_REGISTRY)"
else
	docker login -u gitlab-ci-token -p $(CI_BUILD_TOKEN) $(CI_REGISTRY)
endif

build:
	docker-compose build

push:
	docker-compose push

build-%:
	docker-compose build $*

push-%:
	docker-compose build $*

ci:
	gitlab-runner exec shell ${action}

.PHONY:
	deploy
