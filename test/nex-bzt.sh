#!/bin/bash
# to ensure if 1 command fails.. build fail

# ensure prefix is pass in
if [ $# -lt 1 ] ; then
	echo "nex-bzt.sh needs prefix"
	echo "eg: nex-bzt.sh local|url"
    echo "eg: nex-bzt.sh local numOfuser hold_time ramp_up"
    echo "eg: nex-bzt.sh local 10 2h 3m"
    echo "      means 10 users, run for 2 hours and use 3 min to ramp up"
	exit
fi

PREFIX=$1

if [ "${PREFIX}" != "local" ]; then
    echo "Production Performance Test in CF"
    STD_APP_URL=${PREFIX}
else
    echo "Local Performance Test"
    STD_APP_URL=http://localhost:8000
fi

if [ -z "$2" ]; then
	NO_USERS=3
else
	NO_USERS=$2
fi

if [ -z "$3" ]; then
	HOLD=3m
else
	HOLD="$3"
fi

if [ -z "$4" ]; then
	RAMP_UP=1m
else
	RAMP_UP="$4"
fi

DATA_SRC=./test/nex-users.csv

echo "Starting with ${NO_USERS} user(s) in ${RAMP_UP} min, will run for ${HOLD} hours"
bzt -report -o scenarios.nex.default-address=${STD_APP_URL} \
    -o scenarios.nex.variables.apigee_client_id=client_id \
    -o scenarios.nex.variables.apigee_client_secret=client_secret \
    -o scenarios.nex.data-sources.0=${DATA_SRC} \
    -o execution.0.concurrency=${NO_USERS} \
    -o execution.0.hold-for=${HOLD} \
    -o execution.0.ramp-up=${RAMP_UP} \
    -o modules.console.disable=true \
    -o settings.artifacts-dir=$(mktemp -d -t bzt.XXXX) \
    ./test/nex-bzt.yml
