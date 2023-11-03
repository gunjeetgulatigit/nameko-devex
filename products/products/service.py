import logging

from nameko.events import event_handler
from nameko.rpc import rpc

from products import dependencies, schemas
from products.exceptions import NotFound
from products.productExceptions import ProductNotFound


logger = logging.getLogger(__name__)


class ProductsService:
    name = "products"

    storage = dependencies.Storage()

    @rpc
    def get(self, product_id):
        product = self.storage.get(product_id)
        return schemas.Product().dump(product).data

    @rpc
    def list(self):
        products = self.storage.list()
        return schemas.Product(many=True).dump(products).data

    @rpc
    def create(self, product):
        product = schemas.Product(strict=True).load(product).data
        self.storage.create(product)

    @rpc
    def delete(self, product_id):
        """
        Delete a product from the data store based on its product ID.

        Args:
            product_id (str): The unique product ID to be deleted.

        Raises:
            NotFound: If the product with the specified product ID does not exist.

        Returns:
            None
        """
        try:
            self.storage.delete(product_id)
        except NotFound as error:
            raise ProductNotFound(str(error))

    @event_handler("orders", "order_created")
    def handle_order_created(self, payload):
        for product in payload["order"]["order_details"]:
            self.storage.decrement_stock(product["product_id"], product["quantity"])
