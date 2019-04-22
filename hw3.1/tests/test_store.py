import unittest
from unittest.mock import patch, MagicMock

import fakeredis

from store import Store, RedisStorage


class TestStore(unittest.TestCase):
    def setUp(self):
        self.redis_storage = RedisStorage()
        self.redis_storage.db.connected = False
        self.store = Store(self.redis_storage)
        self.key = 'key1'
        self.value = 'value1'

    @patch('redis.StrictRedis', fakeredis.FakeStrictRedis)
    def test_store_connected(self):
        self.assertTrue(self.store.storage.set(self.key, self.value))
        self.assertEqual(self.store.get(self.key), self.value)

    @patch('redis.StrictRedis', fakeredis.FakeStrictRedis)
    def test_store_disconnected(self):
        self.redis_storage.db.get = MagicMock(side_effect=ConnectionError())

        self.assertRaises(ConnectionError, self.store.get, self.key)
        self.assertEqual(self.redis_storage.db.get.call_count, Store.max_retries)

    @patch('redis.StrictRedis', fakeredis.FakeStrictRedis)
    def test_cache_connected(self):
        self.assertTrue(self.store.cache_set(self.key, self.value))
        self.assertEqual(self.store.cache_get(self.key), self.value)

    @patch('redis.StrictRedis', fakeredis.FakeStrictRedis)
    def test_cache_disconnected(self):
        self.redis_storage.db.get = MagicMock(side_effect=ConnectionError())
        self.redis_storage.db.set = MagicMock(side_effect=ConnectionError())

        self.assertEqual(self.store.cache_get(self.key), None)
        self.assertEqual(self.store.cache_set(self.key, self.value), None)
        self.assertEqual(self.redis_storage.db.get.call_count, Store.max_retries)
        self.assertEqual(self.redis_storage.db.set.call_count, Store.max_retries)