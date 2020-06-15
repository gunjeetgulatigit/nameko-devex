#!/bin/bash

# at least 1 argument to be pass in
if  [ $# == 0 ]; then
    echo "run.sh needs a service module package to run"
    echo "eg: run.sh gate.service api.service"
    exit 1
fi

# Run Migrations for Postgres DB for Orders' backing service 
(
    cd orders
    PYTHONPATH=. alembic upgrade head
)
export PYTHONPATH=./gateway:./orders:./products
nameko show-config

if [ -n "${DEBUG}" ]; then
    echo "nameko service in debug mode. please connect to port 5678 to start service"
    GEVENT_SUPPORT=True python -m debugpy --listen 5678 --wait-for-client run_nameko.py run --config config.yaml $@
else
    python run_nameko.py run --config config.yaml $@
fi
