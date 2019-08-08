import os
import unittest
from unittest.mock import MagicMock

from store import Store, RedisStorage


@unittest.skipIf(
    not (os.getenv('REDIS_HOST') and os.getenv('REDIS_PORT')),
    'Require "REDIS_HOST" and "REDIS_PORT" environment variables'
)
class TestStore(unittest.TestCase):
    def setUp(self):
        self.redis_storage = RedisStorage(host=os.getenv('REDIS_HOST'),
                                          port=int(os.getenv('REDIS_PORT')))
        self.store = Store(self.redis_storage)
        self.key = 'key1'
        self.value = 'value1'

    def test_store_connected(self):
        self.assertTrue(self.store.storage.set(self.key, self.value))
        self.assertEqual(self.store.get(self.key), self.value)

    def test_store_disconnected(self):
        self.redis_storage.db.get = MagicMock(side_effect=ConnectionError())

        self.assertRaises(ConnectionError, self.store.get, self.key)
        self.assertEqual(self.redis_storage.db.get.call_count, Store.max_retries)

    def test_cache_connected(self):
        self.assertTrue(self.store.cache_set(self.key, self.value))
        self.assertEqual(self.store.cache_get(self.key), self.value)

    def test_cache_disconnected(self):
        self.redis_storage.db.get = MagicMock(side_effect=ConnectionError())
        self.redis_storage.db.set = MagicMock(side_effect=ConnectionError())

        self.assertEqual(self.store.cache_get(self.key), None)
        self.assertEqual(self.store.cache_set(self.key, self.value), None)
        self.assertEqual(self.redis_storage.db.get.call_count, Store.max_retries)
        self.assertEqual(self.redis_storage.db.set.call_count, Store.max_retries)
