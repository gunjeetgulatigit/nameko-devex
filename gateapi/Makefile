build-image:
	docker build -t nameko/nameko-example-gateapi:$(TAG) .;

docker-tag:
	docker tag nameko/nameko-example-gateapi:$(FROM_TAG) \
	nameko/nameko-example-gateapi:$(TAG)

push-image:
	docker push nameko/nameko-example-gateapi:$(TAG)
