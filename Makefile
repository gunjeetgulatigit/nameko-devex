PREFIX ?= localdev
HTMLCOV_DIR ?= htmlcov
TAG ?= dev
IMAGES := orders products gateway

CF_ORG ?= good
CF_SPACE ?= morning
CF_APP ?= nameko-devex

install-dependencies:
	pip install -U -e "orders/.[dev]"
	pip install -U -e "products/.[dev]"
	pip install -U -e "gateway/.[dev]"

# test

coverage-html:
	coverage html -d $(HTMLCOV_DIR) --fail-under 100

coverage-report:
	coverage report -m

test:
	flake8 orders products gateway
	coverage run -m pytest gateway/test $(ARGS)
	coverage run --append -m pytest orders/test $(ARGS)
	coverage run --append -m pytest products/test $(ARGS)

coverage: test coverage-report coverage-html

# test
smoke-test:
	./test/nex-smoketest.sh http://localhost:8000

perf-test:
	./test/nex-bzt.sh http://localhost:8000

# docker

build-base:
	docker build --target base -t nameko-example-base .;
	docker build --target builder -t nameko-example-builder .;

build: build-base
	for image in $(IMAGES) ; do TAG=$(TAG) make -C $$image build-image; done

deploy-docker: build
	bash -c "trap 'make undeploy-docker' EXIT; PREFIX=${PREFIX} TAG=$(TAG) docker-compose up"

undeploy-docker:
	PREFIX=$(PREFIX) docker-compose down
	
docker-save:
	mkdir -p docker-images
	docker save -o docker-images/examples.tar $(foreach image,$(IMAGES),nameko/nameko-example-$(image):$(TAG))

docker-load:
	docker load -i docker-images/examples.tar

docker-tag:
	for image in $(IMAGES) ; do make -C $$image docker-tag; done

docker-login:
	docker login --password=$(DOCKER_PASSWORD) --username=$(DOCKER_USERNAME)

push-images:
	for image in $(IMAGES) ; do make -C $$image push-image; done

# cf
cf_target:
	cf target -o $(CF_ORG) -s $(CF_SPACE)

cf_cs_postgres:
	cf cs postgresql 11-7-0 $(CF_APP)_postgres
	echo "Waiting for service to be created"
	for i in $$(seq 1 90); do \
		cf service $(CF_APP)_postgres | grep  "create succeeded" 2> /dev/null && break; \
			sleep 1; \
	done 

cf_ds_postgres:
	cf ds $(CF_APP)_postgres -f
	echo "Waiting for service to be deleted"
	for i in $$(seq 1 90); do \
		cf service $(CF_APP)_postgres | grep  "delete in progress" 2> /dev/null || break; \
			sleep 1; \
	done 

cf_cs_rabbitmq:
	cf cs rabbitmq 3-8-1 $(CF_APP)_rabbitmq
	echo "Waiting for service to be created"
	for i in $$(seq 1 90); do \
		cf service $(CF_APP)_rabbitmq | grep  "create succeeded" 2> /dev/null && break; \
			sleep 1; \
	done 

cf_ds_rabbitmq:
	cf ds $(CF_APP)_rabbitmq -f
	echo "Waiting for service to be deleted"
	for i in $$(seq 1 90); do \
		cf service $(CF_APP)_rabbitmq | grep  "delete in progress" 2> /dev/null || break; \
			sleep 1; \
	done 

cf_cs_redis:
	cf cs redis 5-0-7 $(CF_APP)_redis
	echo "Waiting for service to be created"
	for i in $$(seq 1 90); do \
		cf service $(CF_APP)_redis | grep  "create succeeded" 2> /dev/null && break; \
			sleep 1; \
	done 

cf_ds_redis:
	cf ds $(CF_APP)_redis -f
	echo "Waiting for service to be deleted"
	for i in $$(seq 1 90); do \
		cf service $(CF_APP)_redis | grep  "delete in progress" 2> /dev/null || break; \
			sleep 1; \
	done 

deployCF: cf_target cf_cs_postgres cf_cs_rabbitmq cf_cs_redis
	cf delete $(CF_APP) -f
	# create environment.yml file from environment_dev.yml file
	cat environment_dev.yml | grep -v '#dev' > environment.yml
	cf push $(CF_APP) --no-start
	rm -f environment.yml

	cf bind-service $(CF_APP) $(CF_APP)_postgres
	cf bind-service $(CF_APP) $(CF_APP)_rabbitmq
	cf bind-service $(CF_APP) $(CF_APP)_redis
	cf start $(CF_APP)

undeployCF: cf_target 
	cf delete $(CF_APP) -f -r
	$(MAKE) cf_ds_postgres
	$(MAKE) cf_ds_rabbitmq
	$(MAKE) cf_ds_redis
