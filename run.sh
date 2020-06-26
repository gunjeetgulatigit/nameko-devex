#!/bin/bash

# at least 1 argument to be pass in
if  [ $# == 0 ]; then
    echo "run.sh needs a service module package to run"
    echo "eg: run.sh gate.service orders.service products.service"
    exit 1
fi

# Setup env if not available
export PYTHONPATH=./gateway:./orders:./products

if [ -n "${AMQP_URI}" ]; then
	echo "Using DEV Environment variables.."
    echo 
else
	echo "Using Production Environment Variables in CF.."
    AMQP_URI=$(echo ${VCAP_SERVICES} | jq -r '.cloudamqp[0].credentials.uri')
    POSTGRES_URI=$(echo ${VCAP_SERVICES} | jq -r '.elephantsql[0].credentials.uri')

    REDIS_HOST=$(echo ${VCAP_SERVICES} | jq -r '.rediscloud[0].credentials.hostname')
    REDIS_PORT=$(echo ${VCAP_SERVICES} | jq -r '.rediscloud[0].credentials.port')
    REDIS_PWD=$(echo ${VCAP_SERVICES} | jq -r '.rediscloud[0].credentials.password')
    REDIS_URI=redis://:${REDIS_PWD}@${REDIS_HOST}:${REDIS_PORT}
    echo $AMQP_URI $POSTGRES_URI $REDIS_URI

    export AMQP_URI POSTGRES_URI REDIS_URI
fi



# Run Migrations for Postgres DB for Orders' backing service 
(
    cd orders
    PYTHONPATH=. alembic revision --autogenerate -m "init"
    PYTHONPATH=. alembic upgrade head
)


# nameko show-config

if [ -n "${DEBUG}" ]; then
    echo "nameko service in debug mode. please connect to port 5678 to start service"
    GEVENT_SUPPORT=True python -m debugpy --listen 5678 --wait-for-client run_nameko.py run --config config.yaml $@
else
    python run_nameko.py run --config config.yaml $@
fi
