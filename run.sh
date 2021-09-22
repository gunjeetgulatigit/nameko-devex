#!/bin/bash

# at least 1 argument to be pass in
if  [ $# == 0 ]; then
    echo "run.sh needs a service module package to run"
    echo "eg: run.sh gateway.service orders.service products.service"
    exit 1
fi

# Setup env if not available
export PYTHONPATH=./gateway:./orders:./products

# Check if required env is set, if not exit in errors
REQ_ENVS=(
          AMQP_URI POSTGRES_URI REDIS_URI
        )
TO_EXIT=0
for ENV_NAME in ${REQ_ENVS[@]}; do
        if [ -z $(printenv ${ENV_NAME}) ] || [ "$(printenv ${ENV_NAME})" = "null" ]; then
          echo "Required environment NOT initialized: ${ENV_NAME}"
          TO_EXIT=1
        fi
done
if [ ${TO_EXIT} -eq 1 ]; then
  echo "Above required enivronment(s) is not set properly. Crashing application deliberately"
  exit 1
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
