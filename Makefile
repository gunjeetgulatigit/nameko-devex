PREFIX ?= localdev
HTMLCOV_DIR ?= htmlcov
TAG ?= dev
IMAGES := orders products gateway

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
	./test/nex-smoketest.sh http://localhost:8003

perf-test:
	./test/nex-bzt.sh http://localhost:8003

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
