#!/bin/bash

# Check if rabbit is up and running before starting the service.
# until nc -z ${RABBIT_HOST} ${RABBIT_PORT}; do
#     echo "$(date) - waiting for rabbitmq..."
#     sleep 2
# done

# setting up local environment
export AMQP_URI=amqp://guest:guest@localhost:5672

# Run Service
# uvicorn gateapi.main:app $@
PYTHONPATH=. python gateapi/main.py 