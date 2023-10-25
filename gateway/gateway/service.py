import json

from marshmallow import ValidationError
from nameko import config
from nameko.exceptions import BadRequest
from nameko.rpc import RpcProxy
from werkzeug import Response

from gateway.entrypoints import http
from gateway.exceptions import OrderNotFound, ProductNotFound
from gateway.schemas import CreateOrderSchema, GetOrderSchema, ProductSchema, UpdateProductSchema, \
    ListOrdersRequestSchema, ListOrderResponseSchema


class GatewayService(object):
    """
    Service acts as a gateway to other services over http.
    """

    name = 'gateway'

    orders_rpc = RpcProxy('orders')
    products_rpc = RpcProxy('products')

    @http(
        "GET", "/products/<string:product_id>",
        expected_exceptions=ProductNotFound
    )
    def get_product(self, request, product_id):
        """Gets product by `product_id`
        """
        product = self.products_rpc.get(product_id)
        return Response(
            ProductSchema().dumps(product).data,
            mimetype='application/json'
        )

    @http(
        "PUT", "/products/<string:product_id>",
        expected_exceptions=(ValidationError, BadRequest, ProductNotFound)
    )
    def update_product(self, request, product_id):
        schema = UpdateProductSchema()
        try:
            product_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        if not product_data:
            raise BadRequest("Request must contain valid fields only")

        product_data['id'] = product_id
        self.products_rpc.update(product_data)

        return Response(
            ProductSchema().dumps(product_data).data,
            mimetype='application/json'
        )

    @http(
        "DELETE", "/products/<string:product_id>",
        expected_exceptions=(ValidationError, BadRequest, ProductNotFound)
    )
    def delete_product(self, request, product_id):
        self.products_rpc.delete(product_id)
        return Response(
            None, 204, mimetype='application/json'
        )

    @http(
        "POST", "/products",
        expected_exceptions=(ValidationError, BadRequest)
    )
    def create_product(self, request):
        """Create a new product - product data is posted as json

        Example request ::

            {
                "id": "the_odyssey",
                "title": "The Odyssey",
                "passenger_capacity": 101,
                "maximum_speed": 5,
                "in_stock": 10
            }


        The response contains the new product ID in a json document ::

            {"id": "the_odyssey"}

        """

        schema = ProductSchema(strict=True)

        try:
            # load input data through a schema (for validation)
            # Note - this may raise `ValueError` for invalid json,
            # or `ValidationError` if data is invalid.
            product_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # Create the product
        self.products_rpc.create(product_data)
        return Response(
            json.dumps({'id': product_data['id']}), mimetype='application/json'
        )

    @http("GET", "/orders/<int:order_id>", expected_exceptions=OrderNotFound)
    def get_order(self, request, order_id):
        """Gets the order details for the order given by `order_id`.

        Enhances the order details with full product details from the
        products-service.
        """
        order = self._get_order(order_id)
        return Response(
            GetOrderSchema().dumps(order).data,
            mimetype='application/json'
        )

    def _get_order(self, order_id):
        order = self.orders_rpc.get_order(order_id)

        product_ids_in_order = [item['product_id'] for item in order['order_details']]

        product_map = {prod['id']: prod for prod in self.products_rpc.list(product_ids_in_order)}

        image_root = config['PRODUCT_IMAGE_ROOT']

        for item in order['order_details']:
            product_id = item['product_id']
            item['product'] = product_map[product_id]
            item['image'] = '{}/{}.jpg'.format(image_root, product_id)

        return order

    @http(
        "POST", "/orders",
        expected_exceptions=(ValidationError, ProductNotFound, BadRequest)
    )
    def create_order(self, request):
        """Create a new order - order data is posted as json

        Example request ::

            {
                "order_details": [
                    {
                        "product_id": "the_odyssey",
                        "price": "99.99",
                        "quantity": 1
                    },
                    {
                        "price": "5.99",
                        "product_id": "the_enigma",
                        "quantity": 2
                    },
                ]
            }


        The response contains the new order ID in a json document ::

            {"id": 1234}

        """

        schema = CreateOrderSchema(strict=True)

        try:
            # load input data through a schema (for validation)
            # Note - this may raise `ValueError` for invalid json,
            # or `ValidationError` if data is invalid.
            order_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # Create the order
        # Note - this may raise `ProductNotFound`
        id_ = self._create_order(order_data)
        return Response(json.dumps({'id': id_}), mimetype='application/json')

    def _create_order(self, order_data):
        # check order product ids are valid
        valid_product_ids = {prod['id'] for prod in self.products_rpc.list()}
        for item in order_data['order_details']:
            if item['product_id'] not in valid_product_ids:
                raise ProductNotFound(
                    "Product Id {}".format(item['product_id'])
                )

        # Call orders-service to create the order.
        # Dump the data through the schema to ensure the values are serialized
        # correctly.
        serialized_data = CreateOrderSchema().dump(order_data).data
        result = self.orders_rpc.create_order(
            serialized_data['order_details']
        )
        return result['id']

    @http("GET", "/orders", expected_exceptions=BadRequest)
    def list_orders(self, request):
        data = request.get_data(as_text=True) or "{}"
        try:
            validated_data = ListOrdersRequestSchema().loads(data).data
            ids = validated_data.get("ids")
            page = validated_data.get("page")
            per_page = validated_data.get("per_page")
        except ValidationError as error:
            raise BadRequest("Validation error: {}".format(error))
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        orders = self._list_orders(ids, page, per_page)
        return Response(
            ListOrderResponseSchema(many=True).dumps(orders).data,
            mimetype='application/json'
        )

    def _list_orders(self, ids=None, page=1, per_page=10):
        # Retrieve orders based on ids from the orders service.
        orders = self.orders_rpc.list_orders(ids, page, per_page)

        # For each order, enhance its details.
        for order in orders:
            image_root = config['PRODUCT_IMAGE_ROOT']
            for item in order['order_details']:
                product_id = item['product_id']
                item['image'] = '{}/{}.jpg'.format(image_root, product_id)

        return orders
