NAME=gsicrawler

DEVPORT=8080

KUBE_CA_PEM_FILE=""
KUBE_URL=""
KUBE_TOKEN=""
KUBE_NAMESPACE=$(NAME)
KUBECTL=docker run --rm -v $(KUBE_CA_PEM_FILE):/tmp/ca.pem -v $$PWD:/tmp/cwd/ -i lachlanevenson/k8s-kubectl --server="$(KUBE_URL)" --token="$(KUBE_TOKEN)" --certificate-authority="/tmp/ca.pem" -n $(KUBE_NAMESPACE)
CI_REGISTRY=docker.io
CI_REGISTRY_USER=gitlab
CI_BUILD_TOKEN=""
CI_COMMIT_REF_NAME=master

deploy:
	@$(KUBECTL) delete secret $(CI_REGISTRY) || true
	@$(KUBECTL) create secret docker-registry $(CI_REGISTRY) --docker-server=$(CI_REGISTRY) --docker-username=$(CI_REGISTRY_USER) --docker-email=$(CI_REGISTRY_USER) --docker-password=$(CI_BUILD_TOKEN)
	@$(KUBECTL) apply -f /tmp/cwd/k8s/

.PHONY:
	deploy
