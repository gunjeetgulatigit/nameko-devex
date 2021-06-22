#!/bin/bash

# setting up cf environment
echo "Using Production Environment Variables in CF.."

AMQP_URI=$(echo ${VCAP_SERVICES} | jq -r '.cloudamqp[0].credentials.uri')
POSTGRES_URI=$(echo ${VCAP_SERVICES} | jq -r '.elephantsql[0].credentials.uri')

REDIS_HOST=$(echo ${VCAP_SERVICES} | jq -r '.rediscloud[0].credentials.hostname')
REDIS_PORT=$(echo ${VCAP_SERVICES} | jq -r '.rediscloud[0].credentials.port')
REDIS_PWD=$(echo ${VCAP_SERVICES} | jq -r '.rediscloud[0].credentials.password')
REDIS_URI=redis://:${REDIS_PWD}@${REDIS_HOST}:${REDIS_PORT}

./run.sh $@ 