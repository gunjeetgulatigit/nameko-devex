# Deploying nameko-devex
![Airship Ltd](airship.png)

## Docker
### Prerequisites deployment to Docker
* [docker-for-desktop](https://docs.docker.com/docker-for-mac/) with Kubernetes enabled. 
* Docker cli is working. eg: `docker compose`

### Setup
* Deploy nameko microservice in docker
```sh
make deploy-docker
```
* Smoketest your landscape via `make smoke-test`, make sure you are in your _namekoexample_ conda environment 
* You could also performance test your landscape via `make perf-test`
* To undeploy/stop, Control-C above process

Please read the [Makefile](Makefile) for more details on the commands

## Cloudfoundry / Tanzu
### Prerequisites deployment to CloudFoundry

* [CF cli](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html#pkg)
```ssh
$ brew install cloudfoundry/tap/cf-cli
```
* Get CloudFoundry Landscape:
    - [**Pivotal/VMWare Tanzu**](https://account.run.pivotal.io/z/uaa/sign-up)
    - [IBM Bluemix](https://cloud.ibm.com/registration)
    - [SAP Cloud](https://www.sap.com/cmp/td/sap-cloud-platform-trial.html)
* or Create your own in AWS/Azure:
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
$ conda activate namekoexample
```

* Deploy to CF
```ssh
(namekoexample) devops/nex-deploy.sh <prefix>
```
If prefix is `demo`, the above command will:
- Create the following free backing service instances
  * `demo-rabbitmq` for messaging
  * `demo-postgres` for postgres (Order service)
  * `demo-redis` for redis (Products service)
- Deploy app(s) define in `manifest.yml` with:
  * App name: `demo-namekoexample`
  * URL: `demo-namekoexample.cfapps.io`

For multiple app deployment, uncomment appropriately in `manifest.yml` 

* Undeploy apps from CF
```ssh
(namekoexample) devops/nex-undeploy.sh <prefix>
```

* Verifying app works in CF
```ssh
(namekoexample) test/nex-smoketest.sh <cf_url>
```

### CI/CD
Using Cloudfoundry CLI is so straightforward that creating automation for development in dev or production environment is trivial from developer point of view