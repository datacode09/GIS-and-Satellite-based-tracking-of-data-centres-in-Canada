import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile
import unittest
import config


class TestStatsAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        config.DATABASE = self.tmp.name
        self.tmp.close()
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(config.DATABASE)

    def test_summary(self):
        resp = self.client.get('/api/stats/summary')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('total_dcs', data)
        self.assertGreater(data['total_dcs'], 30)
        self.assertIn('by_province', data)
        self.assertIn('by_size', data)
        self.assertIn('by_operator', data)
        self.assertIn('by_decade', data)

    def test_summary_province_keys(self):
        resp = self.client.get('/api/stats/summary')
        data = resp.get_json()
        self.assertIn('ON', data['by_province'])
        self.assertIn('QC', data['by_province'])
        self.assertIn('BC', data['by_province'])

    def test_operators_list(self):
        resp = self.client.get('/api/stats/operators')
        self.assertEqual(resp.status_code, 200)
        operators = resp.get_json()
        self.assertIsInstance(operators, list)
        self.assertIn('Equinix', operators)

    def test_provinces_list(self):
        resp = self.client.get('/api/stats/provinces')
        self.assertEqual(resp.status_code, 200)
        provinces = resp.get_json()
        self.assertIsInstance(provinces, list)
        codes = [p['province'] for p in provinces]
        self.assertIn('ON', codes)

    def test_health(self):
        resp = self.client.get('/api/health')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('dc_count', data)
