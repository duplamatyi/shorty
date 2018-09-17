import unittest

from werkzeug.test import Client
from werkzeug.testapp import test_app
from shorty import Shorty, create_app
from werkzeug.wrappers import BaseResponse

import redis
from mock import patch
from mockredis import mock_redis_client

from shorty import Shorty

class TestShorty(unittest.TestCase):
    def setUp(self):
        redis_patcher = patch('redis.Redis', mock_redis_client)
        self.redis = redis_patcher.start()
        self.addCleanup(redis_patcher.stop)
        self.redis = redis.Redis()
        self.shorty = Shorty({'redis': self.redis})

    def test_insert_url(self):
        self.assertEqual(self.shorty.insert_url('https://example.com/'), 'c51d')
        self.assertEqual(self.redis.get('url-target:c51d'), b'https://example.com/')
        self.assertEqual(self.redis.get('reverse-url:https://example.com/'), b'c51d')

    def test_insert_new_url(self):
        with patch.object(self.shorty, 'crc16') as mock:
            self.shorty.insert_url('https://example.com/')
        mock.assert_called_once_with('https://example.com/')

    def test_insert_existing_url(self):
        self.redis.set('reverse-url:https://example.com/', 'c51d')
        with patch.object(self.shorty, 'crc16') as mock:
              self.shorty.insert_url('https://example.com/')
        assert not mock.called

if __name__ == '__main__':
    unittest.main()
