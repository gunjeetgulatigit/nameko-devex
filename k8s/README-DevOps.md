# Run Nameko Examples on Kubernetes with MAKE 

![Nameko loves Kubernetes](nameko-k8s.png)

For details of how to use native Helm and Kubectl, please read the original [README.md]

This README-DevOps.md documents how to use MAKE to automate the full deployment of this repo into just a few commands. Please read the [Makefile](Makefile) for more details.

Tested with Kubernetes v1.21.1

## Prerequisites

Please make sure these are installed and working

* [docker-for-desktop](https://docs.docker.com/docker-for-mac/) with Kubernetes enabled. Docker Desktop for Mac is used in these examples but any other Kubernetes cluster will work as well.
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - should be installed and configured during docker-for-desktop installation
* [Helm](https://docs.helm.sh/using_helm/#installing-helm) via `brew install helm`

## Deploy nameko K8S

This will create a namespace, deploy all backing services, deploy ingress, deploy nameko microservices
```sh
make deployK8   
```
Verify your install via `make list-charts` and you should see
```sh
helm --kube-context=docker-desktop list --namespace=examples
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                   APP VERSION
broker          examples        1               2021-06-22 11:19:52.490615 -0700 PDT    deployed        rabbitmq-6.18.2         3.8.2      
cache           examples        1               2021-06-22 11:19:59.757244 -0700 PDT    deployed        redis-10.5.7            5.0.7      
db              examples        1               2021-06-22 11:19:56.178077 -0700 PDT    deployed        postgresql-8.6.4        11.7.0     
gateway         examples        1               2021-06-22 11:20:16.765878 -0700 PDT    deployed        gateway-0.1.0                      
orders          examples        1               2021-06-22 11:20:19.06668 -0700 PDT     deployed        orders-0.1.0                       
products        examples        1               2021-06-22 11:20:21.267799 -0700 PDT    deployed        products-0.1.0 
```

OR via `make get-pods` and you should see:
```sh
kubectl --context=docker-desktop --namespace examples get pods
NAME                        READY   STATUS    RESTARTS   AGE
broker-rabbitmq-0           1/1     Running   0          23m
cache-redis-master-0        1/1     Running   0          23m
cache-redis-slave-0         1/1     Running   0          23m
cache-redis-slave-1         1/1     Running   0          22m
db-postgresql-0             1/1     Running   0          23m
gateway-559b479fc6-b42n5    1/1     Running   0          22m
orders-5b8cfd54b7-5cjhw     1/1     Running   0          22m
products-6f979cb8fb-5lbvj   1/1     Running   0          22m
```

## Deploy nameko into K8S

Smoketest your landscape via `make smoke-test`, make sure you are in your _namekoexample_ conda environment 

You could also performance test your landscape via `make perf-test`

## Undeploy nameko from K8S

You can undeploy your full landscape via `make undeployK8`


