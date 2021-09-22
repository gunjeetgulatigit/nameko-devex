# Run Nameko Examples on Kubernetes

![Nameko loves Kubernetes](nameko-k8s.png)

In this example we'll use local Kubernetes cluster installed with [KinD](https://kind.sigs.k8s.io/) along with community maintained Helm Charts to deploy all 3rd party services. We will also create a set of Helm Charts for Nameko Example Services from this repository.

Below describe the manual step-by-step instructions for deploying into K8S. A scripted version of this instructions can be found [here](../README-DevOps.md)

Tested with Kubernetes v1.21.1

## Prerequisites

Please make sure these are installed and working

* [docker-for-desktop](https://docs.docker.com/docker-for-mac/) or Docker engine in Linux. Kubernetes enabled is not needed since we use KinD as a docker container. KinD is used in these examples but any other Kubernetes cluster will work as well.
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - should be installed and configured
* [Helm](https://docs.helm.sh/using_helm/#installing-helm)

Create Kubernetes cluster using KinD
```ssh
$ export HOST=localhost; export NAMESPACE=nameko; export CONTEXT=kind-${NAMESPACE}
$ kind create cluster --config kind-config.yaml --name ${NAMESPACE}
$ kind export kubeconfig --name ${NAMESPACE}
$ NEWURL=$(kubectl config view | grep -B1 "name: ${CONTEXT}" | grep server: | awk '{print $2}' | sed -e "s/0.0.0.0/${HOST}/")
$ kubectl config set-cluster ${CONTEXT} --server=${NEWURL} --insecure-skip-tls-verify=true 
```

Verify our Kubernetes cluster us up and running:

```sh
$ kubectl --context=kind-nameko get nodes

NAME                   STATUS   ROLES                  AGE     VERSION
nameko-control-plane   Ready    control-plane,master   4m10s   v1.21.1
```

## Create Namespace

It's a good practice to create a namespaces where all of our services will live:

```yaml
# namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: examples
```

```sh
$ kubectl --context=kind-nameko apply -f namespace.yaml

namespace/examples created
```

## Install External Dependencies

Our examples depend on PostgreSQL, Redis and RabbitMQ. 
The fastest way to install these 3rd party dependencies is to use community maintained [Helm Charts](https://github.com/kubernetes/charts).

Let's verify that Helm client is installed

```sh
$ helm version --kube-context=kind-nameko

version.BuildInfo{Version:"v3.6.1", GitCommit:"61d8e8c4a6f95540c15c6a65f36a6dd0a45e7a2f", GitTreeState:"dirty", GoVersion:"go1.16.5"}
```

### Deploy RabbitMQ, PostgreSQL and Redis

Run these commands one by one:

```sh
$ helm --kube-context=kind-nameko install broker  --namespace nameko stable/rabbitmq

$ helm --kube-context=kind-nameko install db --namespace nameko stable/postgresql --set postgresqlDatabase=orders

$ helm --kube-context=kind-nameko install cache  --namespace nameko stable/redis
```

RabbitMQ, PostgreSQL and Redis are now installed along with persistent volumes, kubernetes services, config maps and any secrets required a.k.a. `Amazing™`!

Verify all pods are running:

```sh
$ kubectl --context=kind-nameko --namespace=nameko get pods

NAME                   READY   STATUS    RESTARTS   AGE
broker-rabbitmq-0      1/1     Running   0          80s
cache-redis-master-0   1/1     Running   0          54s
cache-redis-slave-0    1/1     Running   0          54s
cache-redis-slave-1    1/1     Running   0          10s
db-postgresql-0        1/1     Running   0          62s
```

## Deploy Example Services

To deploy our example services, we'll have to create Kubernetes deployment definition files. 
Most of the time (in real world) you would want to use some dynamic data during your deployments e.g. define image tags.
The easiest way to do this is to create Helm Charts for each of our service and use Helm to deploy them. 

Our charts are organized as follows:

```txt
charts
├── gateway
│   ├── Chart.yaml
│   ├── templates
│   │   ├── NOTES.txt
│   │   ├── deployment.yaml
│   │   ├── ingress.yaml
│   │   └── service.yaml
│   └── values.yaml
├── orders
│   ├── Chart.yaml
│   ├── templates
│   │   ├── NOTES.txt
│   │   └── deployment.yaml
│   └── values.yaml
└── products
    ├── Chart.yaml
    ├── templates
    │   ├── NOTES.txt
    │   └── deployment.yaml
    └── values.yaml
```

Each chart is comprised of:

`Charts.yaml` file containing description of the chart.  
`values.yaml` file containing default values for a chart that can be overwritten during the release..  
`templates` folder where all Kubernetes definition files live.

All of our charts contain `deployment.yaml` template where main Nameko Service deployment definition lives. `Gateway` chart has additional definitions for `ingress` and kubernetes `service` which are required to enable inbound traffic.

Example of products `deployment.yaml`:

```yaml
apiVersion: apps/v1beta2
kind: Deployment
metadata:
  name: {{ .Chart.Name }}
  labels:
    app: {{ .Chart.Name }}
    tag: {{ .Values.image.tag }}
    revision: "{{ .Release.Revision }}"
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
      - image: nameko/nameko-example-products:{{ .Values.image.tag }}
        name: {{ .Chart.Name }}
        env:
          - name: REDIS_HOST
            value: cache-redis-master
          - name: REDIS_INDEX
            value: "11"
          - name: REDIS_PORT
            value: "6379"
          - name: REDIS_PASSWORD
            valueFrom:
              secretKeyRef:
                name: cache-redis
                key: redis-password
          - name: RABBIT_HOST
            value: broker-rabbitmq
          - name: RABBIT_MANAGEMENT_PORT
            value: "15672"
          - name: RABBIT_PORT
            value: "5672"
          - name: RABBIT_USER
            value: user
          - name: RABBIT_PASSWORD
            valueFrom:
              secretKeyRef:
                name: broker-rabbitmq
                key: rabbitmq-password
      restartPolicy: Always

```

As you can see this template is using values coming from `Chart` and `Values` files as well as dynamic `Release` information. Passwords from secrets created by Redis and RabbitMQ releases are also referenced and passed to a container as `REDIS_PASSWORD` and `RABBIT_PASSWORD` environment variables respectively.

Please read [The Chart Template Developer’s Guide](https://docs.helm.sh/chart_template_guide/#the-chart-template-developer-s-guide)
to learn about creating your own charts.

To route traffic to our gateway service we'll be using ingress. For ingress to work `Ingress Controller` has to be enabled on our cluster. Follow instructions form [Ingress Installation docs](https://kind.sigs.k8s.io/docs/user/ingress/):

```sh
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
$ kubectl wait --namespace ingress-nginx \
		--for=condition=ready pod \
		--selector=app.kubernetes.io/component=controller \
		--timeout=90s
```

Let's deploy our `products` chart:

```sh
$ helm upgrade products charts/products --install \
    --namespace=nameko --kube-context=kind-nameko \
    --set image.tag=latest

Release "products" does not exist. Installing it now.
NAME: products
LAST DEPLOYED: Wed Sep 22 10:46:05 2021
NAMESPACE: nameko
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing Products Service!
```

We used `--set image.tag=latest` to set custom image tag to be used for this release. You can do the same for any values defined in values.yaml file.

Let's release `orders` and `gateway` services:

```sh
$ helm upgrade orders charts/orders --install \
    --namespace=nameko --kube-context=kind-nameko \
    --set image.tag=latest

Release "orders" does not exist. Installing it now.
(...)

$ helm upgrade gateway charts/gateway --install \
    --namespace=nameko --kube-context=kind-nameko \
    --set image.tag=latest

Release "gateway" does not exist. Installing it now.
(...)
```

Let's list all of our Helm releases:

```sh
$ helm --kube-context=kind-nameko list --namespace nameko

NAME    	REVISION	UPDATED                 	STATUS  	CHART
broker  	1       	Tue Oct 29 06:50:26 2019	DEPLOYED	rabbitmq-4.11.1
cache   	1       	Tue Oct 29 06:50:43 2019	DEPLOYED	redis-6.4.4
db      	1       	Tue Oct 29 06:50:35 2019	DEPLOYED	postgresql-3.16.1
gateway 	1       	Tue Oct 29 06:54:09 2019	DEPLOYED	gateway-0.1.0
orders  	1       	Tue Oct 29 06:54:01 2019	DEPLOYED	orders-0.1.0
products	1       	Tue Oct 29 06:53:43 2019	DEPLOYED	products-0.1.0
```

And again let's verify pods are happily running:

```sh
$ kubectl --context=kind-nameko --namespace=nameko get pods

NAME                        READY   STATUS    RESTARTS   AGE
broker-rabbitmq-0           1/1     Running   0          9m48s
cache-redis-master-0        1/1     Running   0          9m22s
cache-redis-slave-0         1/1     Running   0          9m22s
cache-redis-slave-1         1/1     Running   0          8m38s
db-postgresql-0             1/1     Running   0          9m30s
gateway-559b479fc6-8sdb9    1/1     Running   0          2m19s
orders-5b8cfd54b7-s6pm6     1/1     Running   0          2m26s
products-6f979cb8fb-d6w94   1/1     Running   0          3m52s
```

## Run examples

We can now verify our gateway api is working as expected by executing sample requests found in main README of this repository.

#### Create Product

```sh
$ curl -XPOST -d '{"id": "the_odyssey", "title": "The Odyssey", "passenger_capacity": 101, "maximum_speed": 5, "in_stock": 10}' 'http://localhost/products'

{"id": "the_odyssey"}
```

#### Get Product

```sh
$ curl 'http://localhost/products/the_odyssey'

{
  "id": "the_odyssey",
  "title": "The Odyssey",
  "passenger_capacity": 101,
  "maximum_speed": 5,
  "in_stock": 10
}
```
#### Create Order

```sh
$ curl -XPOST -d '{"order_details": [{"product_id": "the_odyssey", "price": "100000.99", "quantity": 1}]}' 'http://localhost/orders'

{"id": 1}
```

#### Get Order

```sh
$ curl 'http://localhost/orders/1'

{
  "id": 1,
  "order_details": [
    {
      "id": 1,
      "quantity": 1,
      "product_id": "the_odyssey",
      "image": "http://www.example.com/airship/images/the_odyssey.jpg",
      "price": "100000.99",
      "product": {
        "maximum_speed": 5,
        "id": "the_odyssey",
        "title": "The Odyssey",
        "passenger_capacity": 101,
        "in_stock": 9
      }
    }
  ]
}
```

## Wrap-up

Running Nameko services in Kubernetes is really simple. Please get familiar with Helm Charts included in this repository and try adding one of your own. 
