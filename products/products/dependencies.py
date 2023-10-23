from nameko import config
from nameko.extensions import DependencyProvider
import redis

from products.exceptions import NotFound


REDIS_URI_KEY = 'REDIS_URI'


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


    def list(self):
        keys = self.client.keys(self._format_key('*'))
        for key in keys:
            yield self._from_hash(self.client.hgetall(key))

    def create(self, product):
        self.client.hmset(
            self._format_key(product['id']),
            product)

    def update(self, product):
        try:
            product_key = self._format_key(product['id'])

            if not self.client.exists(product_key):
                raise NotFound(f'Product ID {product["id"]} does not exist')

            self.client.hmset(product_key, product)

            cache_key = f"cache:{product['id']}"
            self.client.hmset(cache_key, product)
            self.client.expire(cache_key, 3600)

        except redis.RedisError as e:
            raise Exception(f"Error updating product in Redis: {e}")


    def decrement_stock(self, product_id, amount):
        return self.client.hincrby(
            self._format_key(product_id), 'in_stock', -amount)


class Storage(DependencyProvider):

    def setup(self):
        self.client = redis.StrictRedis.from_url(config.get(REDIS_URI_KEY))

    def get_dependency(self, worker_ctx):
        return StorageWrapper(self.client)
