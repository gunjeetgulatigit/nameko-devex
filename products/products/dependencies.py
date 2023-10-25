from nameko import config
from nameko.extensions import DependencyProvider
import redis
import logging

from products.exceptions import NotFound, InvalidOperation

REDIS_URI_KEY = 'REDIS_URI'

logger = logging.getLogger(__name__)

class StorageWrapper:
    """
    Product storage

    A very simple example of a custom Nameko dependency. Simplified
    implementation of products database based on Redis key value store.
    Handling the product ID increments or keeping sorted sets of product
    names for ordering the products is out of the scope of this example.

    """
    NotFound = NotFound

    def __init__(self, client):
        self.client = client

    def _format_key(self, product_id):
        return 'products:{}'.format(product_id)

    def _from_hash(self, document):
        return {
            'id': document[b'id'].decode('utf-8'),
            'title': document[b'title'].decode('utf-8'),
            'passenger_capacity': int(document[b'passenger_capacity']),
            'maximum_speed': int(document[b'maximum_speed']),
            'in_stock': int(document[b'in_stock'])
        }


    def get(self, product_id):
        cache_key = f"cache:{product_id}"
        product = self.client.hgetall(cache_key)

        if not product:
            product = self.client.hgetall(self._format_key(product_id))

        if product:
            self.client.hmset(cache_key, product)
            self.client.expire(cache_key, 3600)
        else:
            raise NotFound(f'Product ID {product_id} does not exist')

        return self._from_hash(product)


    def list(self, product_ids=None):
        if product_ids and not isinstance(product_ids, list):
            raise ValueError("product_ids must be a list or None")

        if product_ids:
            print("i was here 7")
            keys = [self._format_key(product_id) for product_id in product_ids]
        else:
            keys = self.client.keys(self._format_key('*'))

        for key in keys:
            product_data = self.client.hgetall(key)
            if product_data:
                yield self._from_hash(product_data)


    def create(self, product):
        self.client.hmset(
            self._format_key(product['id']),
            product)

    def update(self, product):
        try:
            product_key = self._format_key(product['id'])

            self.client.hmset(product_key, product)

            cache_key = f"cache:{product['id']}"
            self.client.hmset(cache_key, product)
            self.client.expire(cache_key, 3600)

        except redis.RedisError as e:
            raise Exception(f"Error updating product in Redis: {e}")


    def delete(self, product_id):
        print(f"Deleting product {product_id}")
        cache_key = f"cache:{product_id}"
        product_key = self._format_key(product_id)

        product_in_cache = self.client.hgetall(cache_key)

        if not product_in_cache:
            product_in_storage = self.client.hgetall(product_key)
            if not product_in_storage:
                raise NotFound(f'Product ID {product_id} does not exist')

        self.client.delete(cache_key)
        self.client.delete(product_key)


    def decrement_stock(self, product_id, amount):
        current_stock = int(self.client.hget(self._format_key(product_id), 'in_stock'))
        if current_stock - amount < 0:
            logger.error(f"Attempt to decrement stock below 0 for product ID {product_id}")
            raise InvalidOperation(f"Insufficient stock for product ID {product_id}")

        return self.client.hincrby(
            self._format_key(product_id), 'in_stock', -amount)


class Storage(DependencyProvider):

    def setup(self):
        self.client = redis.StrictRedis.from_url(config.get(REDIS_URI_KEY))

    def get_dependency(self, worker_ctx):
        return StorageWrapper(self.client)
