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
if [ "${PREFIX}" = "local" ] ; then
  	LOCAL_DEV=1
else
	LOCAL_DEV=0
fi

# 1. Get App configuration via CF
if [ "${LOCAL_DEV}" -ne 1 ]; then
    echo "Server Deployment"
	STD_APP_URL="https://${PREFIX}"

else
	STD_APP_URL="http://localhost:8000"
	echo "Local Development"
fi
echo STD_APP_URL=${STD_APP_URL}

# Test: Create Products
echo "=== Creating a product id: the_odyssey ==="
curl -XPOST  "${STD_APP_URL}/products" \
	 -d '{"id": "the_odyssey", "title": "The Odyssey", "passenger_capacity": 101, "maximum_speed": 5, "in_stock": 10}'
echo
# Test: Get Product
echo "=== Getting product id: the_odyssey ==="
curl -s "${STD_APP_URL}/products/the_odyssey" | jq .

# Test: Create Order
echo "=== Creating Order ==="
ORDER_ID=$(curl -s -XPOST -d '{"order_details": [{"product_id": "the_odyssey", "price": "100000.99", "quantity": 1}]}' "${STD_APP_URL}/orders")
echo ${ORDER_ID}
ID=$(echo ${ORDER_ID} | jq '.id')

# Test: Get Order back
echo "=== Getting Order ==="
curl -s "${STD_APP_URL}/orders/${ID}" | jq -r

# Test: List Orders
echo "=== Listing Orders ==="
curl -s "${STD_APP_URL}/orders" | jq .

# Test: Delete Product
echo "=== Deleting product id: the_odyssey ==="
curl -s -X DELETE "${STD_APP_URL}/products/the_odyssey"
echo

# Test: Try to Get the Deleted Product
echo "=== Attempting to Get deleted product id: the_odyssey ==="
curl -s -o /dev/null -w "%{http_code}" "${STD_APP_URL}/products/the_odyssey"
