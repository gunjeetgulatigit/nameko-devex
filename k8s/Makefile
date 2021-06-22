CONTEXT ?= docker-desktop
NAMESPACE ?= examples
TAG ?= latest

# all in one
undeployK8:
	$(MAKE) delete-namespace
	$(MAKE) undeploy-ingress

deployK8:
	$(MAKE) init-helm
	$(MAKE) create-namespace
	$(MAKE) deploy-dependencies
	$(MAKE) deploy-ingress
	$(MAKE) install-charts

# test
smoke-test:
	../test/nex-smoketest.sh http://localhost

perf-test:
	cd ..; ./test/nex-bzt.sh http://localhost

# kubectl short-cuts

get-nodes:
	kubectl --context=$(CONTEXT) --namespace $(NAMESPACE) get nodes

get-pods:
	kubectl --context=$(CONTEXT) --namespace $(NAMESPACE) get pods

get-logs:
	kubectl --context=$(CONTEXT) --namespace $(NAMESPACE) logs -f $(NAME)

create-namespace:
	kubectl --context=$(CONTEXT) apply -f namespace.yaml

delete-namespace:
	kubectl --context=$(CONTEXT) delete -f namespace.yaml

# helm

init-helm:
	helm repo add stable https://charts.helm.sh/stable
	helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
	helm repo update

list-charts:
	helm --kube-context=$(CONTEXT) list --namespace=$(NAMESPACE)

deploy-dependencies:
	helm upgrade broker stable/rabbitmq --install \
	--namespace $(NAMESPACE) --kube-context=$(CONTEXT)
	helm upgrade db stable/postgresql --install \
	--set postgresqlDatabase=orders \
	--namespace $(NAMESPACE) --kube-context=$(CONTEXT)
	helm upgrade cache stable/redis --install \
	--namespace $(NAMESPACE) --kube-context=$(CONTEXT)
	kubectl --context=$(CONTEXT) --namespace=$(NAMESPACE) get pods

deploy-ingress:
	helm upgrade ingress-nginx ingress-nginx/ingress-nginx --install

undeploy-ingress:
	kubectl get pods --namespace default --no-headers=true | awk '{print $$1}' | xargs kubectl --namespace default delete pod

install-charts:
	$(MAKE) SERVICE_NAME=gateway install-chart
	$(MAKE) SERVICE_NAME=orders install-chart
	$(MAKE) SERVICE_NAME=products install-chart

test-charts:
	$(MAKE) SERVICE_NAME=gateway test-chart
	$(MAKE) SERVICE_NAME=orders test-chart
	$(MAKE) SERVICE_NAME=products test-chart

lint-charts:
	$(MAKE) SERVICE_NAME=gateway lint-chart
	$(MAKE) SERVICE_NAME=orders lint-chart
	$(MAKE) SERVICE_NAME=products lint-chart

test-chart:
	helm upgrade $(SERVICE_NAME) charts/$(SERVICE_NAME) --install \
	--namespace=$(NAMESPACE) --kube-context $(CONTEXT) \
	--dry-run --debug --set image.tag=$(TAG)

install-chart:
	helm upgrade $(SERVICE_NAME) charts/$(SERVICE_NAME) --install \
	--namespace=$(NAMESPACE) --kube-context=$(CONTEXT) \
	--set image.tag=$(TAG)

lint-chart:
	helm lint charts/$(SERVICE_NAME) --strict
