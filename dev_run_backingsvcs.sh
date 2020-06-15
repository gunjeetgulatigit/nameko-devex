#!/bin/bash

# Put this in the ~/.bashrc or ~/.zshrc as alias command if you want to start it individually
# alias devRabbit="docker rm -f devRabbit ; docker run -d --name devRabbit -p 5672:5672 -p 5673:5673 -p 15672:15672 rabbitmq:3-management"
# alias devPostgres="docker rm -f devPostgres ; docker run -d --name devPostgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres"
# alias devRedis="docker rm -f devRedis ; docker run -d --name devRedis -p 6379:6379 redis"


docker rm -f devRabbit ; docker run -d --name devRabbit -p 5672:5672 -p 5673:5673 -p 15672:15672 rabbitmq:3-management
docker rm -f devPostgres ; docker run -d --name devPostgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
docker rm -f devRedis ; docker run -d --name devRedis -p 6379:6379 redis

echo all services started