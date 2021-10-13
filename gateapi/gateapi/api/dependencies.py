"""
source reference: https://github.com/tiangolo/fastapi/issues/504#issuecomment-632019696
"""

from nameko.standalone.rpc import ClusterRpcClient
import os
import asyncio
from typing import Optional

AMQP_URI = os.getenv('AMQP_URI')
TIMEOUT = 3

class NamekoRPCPoolDep:
    def __init__(self, amqp_uri, timeout = None):
        self._pool: Optional[ClusterRpcClient] = None
        self._lock = asyncio.Lock()
        self._amqp_uri = amqp_uri
        self._timeout = timeout

    async def __call__(self):
        if self._pool is not None:
            return self._pool

        async with self._lock:
            if self._pool is not None:
                return self._pool
            proxy = ClusterRpcClient(
                uri=self._amqp_uri,
                timeout=self._timeout
            )
            self._pool = proxy.start()

        return self._pool

nameko_rpc = NamekoRPCPoolDep(AMQP_URI)
nameko_pool_timeout = NamekoRPCPoolDep(AMQP_URI,TIMEOUT)
