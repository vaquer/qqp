import falcon
from falcon import testing
from unittest import TestCase
from unittest.mock import mock_open, call
from app import api


class TestPrices(TestCase):
    def setUp(self):
        self.client = testing.TestClient(api)

    def test_get_one_resource(self):
        response = self.client.simulate_get('/prices')

        self.assertEqual(response.status, falcon.HTTP_OK)
        self.assertTrue(type(response.json), dict)

        response = self.client.simulate_get('/prices/12')
        self.assertEqual(response.status, falcon.HTTP_OK)
        self.assertTrue(type(response.json), dict)