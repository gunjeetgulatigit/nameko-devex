#!/bin/bash

# setting up cf environment
echo "Retrieving Production Environment Variables in CF.."

export AMQP_URI=$(echo ${VCAP_SERVICES} | jq -r '.rabbitmq[0].credentials.uri')
export POSTGRES_URI=$(echo ${VCAP_SERVICES} | jq -r '.postgresql[0].credentials.uri')/devex
export REDIS_URI=$(echo ${VCAP_SERVICES} | jq -r '.redis[0].credentials.uri')

# create dbname for postgres

python -c """
import psycopg2 as db
from urllib.parse import urlparse
result = urlparse('${POSTGRES_URI}')
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
con=db.connect(dbname='postgres',host=hostname,user=username,password=password)
con.autocommit=True;con.cursor().execute('CREATE DATABASE devex')
"""

./run.sh $@ 