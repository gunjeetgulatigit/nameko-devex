"""
source reference: https://github.com/nameko/nameko/pull/357
"""
import weakref
import os

from six.moves import xrange as xrange_six, queue as queue_six
from nameko.standalone.rpc import ClusterRpcClient
from nameko import config
from nameko.cli.utils.config import setup_config

class ClusterRpcProxyPool(object):
    """ Connection pool for Nameko RPC cluster.
    Pool size can be customized by passing `pool_size` kwarg to constructor.
    Default size is 2 per uvicorn worker (should be enough)
    *Usage*
        pool = ClusterRpcProxyPool(config)
        pool.start()
        # ...
        with pool.next() as rpc:
            rpc.mailer.send_mail(foo='bar')
        # ...
        pool.stop()
    This class is thread-safe and designed to work with GEvent.
    """
    class RpcContext(object):
        def __init__(self, pool, uri, timeout):
            self.pool = weakref.proxy(pool)
            self.proxy = ClusterRpcClient(uri=uri, timeout=timeout)
            self.rpc = self.proxy.start()

        def stop(self):
            self.proxy.stop()
            self.proxy = None
            self.rpc = None

        def __enter__(self):
            return self.rpc

        def __exit__(self, *args, **kwargs):
            try:
                self.pool._put_back(self)
            except ReferenceError:  # pragma: no cover
                # We're detached from the parent, so this context
                # is going to silently die.
                self.stop()

    def __init__(self, uri, timeout=None, pool_size=2):
        self.uri = uri
        self.timeout = timeout
        self.pool_size = pool_size

    def start(self):
        """ Populate pool with connections.
        """
        self.queue = queue_six.Queue()
        for i in xrange_six(self.pool_size):
            ctx = ClusterRpcProxyPool.RpcContext(self, self.uri, self.timeout)
            self.queue.put(ctx)

    def next(self, timeout=None):
        """ Fetch next connection.
        This method is thread-safe.
        """
        return self.queue.get(timeout=timeout)

    def _put_back(self, ctx):
        self.queue.put(ctx)

    def stop(self):
        """ Stop queue and remove all connections from pool.
        """
        while True:
            try:
                ctx = self.queue.get_nowait()
                ctx.stop()
            except queue_six.Empty:
                break
        self.queue.queue.clear()
        self.queue = None

# Global/Module pool
if os.path.exists('config.yml'):
    with open('config.yml', 'r') as config_file:
        setup_config(config_file)
else:
    raise Exception("config.yml configuration file not found")

NAMEKO_POOL = ClusterRpcProxyPool(
    uri=config['AMQP_URI'],
    timeout=None
)
NAMEKO_POOL.start()

def destroy_nameko_pool():
    NAMEKO_POOL.stop()

def get_rpc():
    yield NAMEKO_POOL

config = config