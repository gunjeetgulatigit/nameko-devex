#!/bin/bash

# Check if rabbit is up and running before starting the service.
until nc -z localhost 5672; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 2
done

# Check if redis is up and running before starting the service.
until nc -z localhost 6379; do
    echo "$(date) - waiting for redis..."
    sleep 2
done

# Check if postgres is up and running before starting the service.
until nc -z localhost 5432; do
    echo "$(date) - waiting for postgres..."
    sleep 2
done

# create database orders locally
python -c """import psycopg2 as db;p='postgres';con=db.connect(dbname=p,host='localhost',user=p,password=p);
con.autocommit=True;con.cursor().execute('CREATE DATABASE orders')""" 2> /dev/null

# setting up local environment
export AMQP_URI=amqp://guest:guest@localhost:5672
export POSTGRES_URI=postgresql://postgres:postgres@localhost:5432/orders
export REDIS_URI=redis://localhost:6379/dev

./run.sh $@ 
