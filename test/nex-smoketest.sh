#!/bin/bash

# DIR="${BASH_SOURCE%/*}"
# if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
# . "$DIR/nex-include.sh"

# to ensure if 1 command fails.. build fail
set -e

# ensure prefix is pass in
if [ $# -lt 1 ] ; then
	echo "NEX smoketest needs prefix"
	echo "nex-smoketest.sh acceptance"
	exit
fi

PREFIX=$1

# check if doing local smoke test
if [ "${PREFIX}" != "local" ]; then
    echo "Remote Smoke Test in CF"
    STD_APP_URL=${PREFIX}
else
    echo "Local Smoke Test"
    STD_APP_URL=http://localhost:8000
fi

echo STD_APP_URL=${STD_APP_URL}

# Test: Create Products
echo "=== Creating a product id: the_odyssey ==="
curl -s -XPOST  "${STD_APP_URL}/products" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"id": "the_odyssey", "title": "The Odyssey", "passenger_capacity": 101, "maximum_speed": 5, "in_stock": 10}'
echo

# Test: Get Product
echo "=== Getting product id: the_odyssey ==="
curl -s "${STD_APP_URL}/products/the_odyssey" | jq .
echo

# Test: Update Product
echo "=== Updating a product id: the_odyssey ==="
UPDATE_RESPONSE=$(curl -s -XPUT  "${STD_APP_URL}/products/the_odyssey" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"title": "New Odyssey", "passenger_capacity": 101, "maximum_speed": 4, "in_stock": 10}')
echo ${UPDATE_RESPONSE} | jq .
echo

# Test: Create Order
echo "=== Creating Order ==="
ORDER_ID=$(
    curl -s -XPOST "${STD_APP_URL}/orders" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"order_details": [{"product_id": "the_odyssey", "price": "100000.99", "quantity": 1}]}' 
)
echo "${ORDER_ID}"
ID=$(echo ${ORDER_ID} | jq '.id')

# Test: Get Order back
echo "=== Getting Order ==="
curl -s "${STD_APP_URL}/orders/${ID}" | jq .

# Test: List All Orders
echo "=== Listing All Orders ==="
curl -s "${STD_APP_URL}/orders" | jq .
echo

echo
# Test: Delete Product
echo "=== Deleting product id: the_odyssey ==="
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -XDELETE "${STD_APP_URL}/products/the_odyssey")
echo "Received HTTP status code: ${HTTP_STATUS}"
echo