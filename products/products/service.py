import logging

from nameko.events import event_handler
from nameko.rpc import rpc

from products import dependencies, schemas


logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()

    @rpc
    def get(self, product_id):
        product = self.storage.get(product_id)
        return schemas.Product().dump(product).data

    @rpc
    def list(self, product_ids=None):
        products = self.storage.list(product_ids)
        return schemas.Product(many=True).dump(products).data

    @rpc
    def create(self, product):
        product = schemas.Product(strict=True).load(product).data
        self.storage.create(product)

    @rpc
    def update(self, product):
        existing_product = self.storage.get(product['id'])
        updated_product = {**existing_product, **product}
        self.storage.update(updated_product)

    @rpc
    def delete(self, product_id):
        self.storage.delete(product_id)

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])
