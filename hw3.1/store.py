import functools
import time

import redis


def retry(attempts=5, silent=True):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for attempt in range(attempts):
                try:
                    return f(*args, **kwargs)
                except (TimeoutError, ConnectionError):
                    time.sleep(1)
            if not silent:
                raise ConnectionError
        return wrapper
    return decorator


class RedisStorage:
    def __init__(self, host='localhost', port=6379, timeout=3, connect_now=True):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.db = None
        if connect_now:
            self.connect()

    def connect(self):
        self.db = redis.Redis(
            host=self.host,
            port=self.port,
            db=0,
            socket_connect_timeout=self.timeout,
            socket_timeout=self.timeout
        )

    def get(self, key):
        try:
            value = self.db.get(key)
            return value.decode() if value else value
        except redis.exceptions.TimeoutError:
            raise TimeoutError
        except redis.RedisError:
            raise ConnectionError

    def set(self, key, value, expires=None):
        try:
            return self.db.set(key, value, ex=expires)
        except redis.exceptions.TimeoutError:
            raise TimeoutError
        except redis.exceptions.ConnectionError:
            raise ConnectionError


class Store:
    max_retries = 5

    def __init__(self, storage):
        self.storage = storage

    @retry(attempts=max_retries, silent=False)
    def get(self, key):
        return self.storage.get(key)

    @retry(attempts=max_retries, silent=True)
    def cache_get(self, key):
        return self.storage.get(key)

    @retry(attempts=max_retries, silent=True)
    def cache_set(self, key, value, expires=None):
        return self.storage.set(key, value, expires)
