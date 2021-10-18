# Deploying nameko-devex
![Airship Ltd](airship.png)

## Docker
### Prerequisites deployment to Docker
* [Docker](https://docs.docker.com/get-docker/). 
* Docker cli is working. eg: `docker-compose` - [Install instructions](https://docs.docker.com/compose/install/)

### Setup
* Deploy nameko microservice in docker
```sh
make deploy-docker
```
* Smoketest your landscape via `make smoke-test`, make sure you are in your _namekoexample_ conda environment 
* You could also performance test your landscape via `make perf-test`
* To undeploy/stop, Control-C above process

Please read the [Makefile](Makefile) for more details on the commands

## K8S using KinD
### Prerequisites deployment to K8S
* Docker (see above)
* Kubernetes in Docker - [KinD](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

### Setup
* Deploy nameko microservice in K8S
```sh
cd k8s
make deployK8
```
* Smoketest your landscape via `make smoke-test`, make sure you are in your _namekoexample_ conda environment 
* You could also performance test your landscape via `make perf-test`
* To undeploy, use `make undeployK8`

Please read the [Makefile](k8s/Makefile) for more details on the commands


## Cloudfoundry
### Prerequisites deployment to CloudFoundry

* [CF cli](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html#pkg)
```ssh
$ brew install cloudfoundry/tap/cf-cli
```
* Get CloudFoundry Landscape:
    - [Pivotal/VMWare Tanzu](https://account.run.pivotal.io/z/uaa/sign-up)
    - [IBM Bluemix](https://cloud.ibm.com/registration)
    - [SAP Cloud](https://www.sap.com/cmp/td/sap-cloud-platform-trial.html)
* or Create your own in AWS/Azure:
    - [**KubeCF in KinD**](https://kubecf.io/docs/tutorials/deploy-kind/)
    - [Tanzu on Azure](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/pivotal.pivotal-cloud-foundry)
    - [Tanzu on Google](https://tanzu.vmware.com/partners/google)
    - [Pivotal Cloud Foundry on AWS](https://aws.amazon.com/quickstart/architecture/pivotal-cloud-foundry/)
* or install your own via Terraform
    - [AWS](https://docs.pivotal.io/platform/ops-manager/2-9/aws/prepare-env-terraform.html)
    - In the above same link, you see scripts for Google and Azure
### Setup
For below instruction, we are assuming you have created a free CF acount from [Pivotal](https://account.run.pivotal.io/z/uaa/). We are using their free backing service from there.

* Login into CF account. Read quick [tutorial](https://docs.cloudfoundry.org/cf-cli/getting-started.html#login)

* Activate environment before running deployment script
```ssh
$ conda activate nameko-devex
```

* Deploy to CF via make
```ssh
(nameko-devex) CF_APP=<prefix> make deployCF
```
If prefix is `demo`, the above command will:
- Create the following free backing service instances
  * `demo_rabbitmq` for messaging
  * `demo_postgres` for postgres (Order service)
  * `demo_redis` for redis (Products service)

- Push `demo` app with _no-start_ option
- Bind `demo` app to each backing service
- Restage/restart `demo` app
- Note: We can use `manifest.yml` for deployment without above step assuming the backing service is create prior
  * URL: `demo.<CF_DOMAIN>`

For multiple app deployment, uncomment appropriately in `manifest.yml` 

* Undeploy apps from CF
```ssh
(nameko-devex) CF_APP=<PREFIX> make undeployCF <prefix>
```

* Verifying app works in CF
```ssh
(nameko-devex) test/nex-smoketest.sh <cf_url>
```

### CI/CD
Using Cloudfoundry CLI is so straightforward that creating automation for development in dev or production environment is trivial from developer point of view