import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile
import unittest
import math
import config
from api.spatial import haversine_km


class TestHaversine(unittest.TestCase):
    def test_same_point(self):
        self.assertAlmostEqual(haversine_km(43.65, -79.38, 43.65, -79.38), 0.0, places=5)

    def test_one_degree_longitude_at_equator(self):
        d = haversine_km(0, 0, 0, 1)
        self.assertAlmostEqual(d, 111.195, delta=0.5)

    def test_van_to_mtl(self):
        d = haversine_km(49.2827, -123.1207, 45.5017, -73.5673)
        self.assertGreater(d, 3500)
        self.assertLess(d, 3900)


class TestSpatialAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        config.DATABASE = self.tmp.name
        self.tmp.close()
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(config.DATABASE)

    def test_bbox_toronto(self):
        resp = self.client.get('/api/spatial/bbox?north=43.9&south=43.5&east=-79.0&west=-79.8')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreater(len(data['features']), 0)

    def test_bbox_missing_params(self):
        resp = self.client.get('/api/spatial/bbox?north=44')
        self.assertEqual(resp.status_code, 400)

    def test_radius_toronto(self):
        resp = self.client.get('/api/spatial/radius?lat=43.65&lon=-79.38&radius_km=5')
        data = resp.get_json()
        ids = [f['properties']['id'] for f in data['features']]
        self.assertGreater(len(ids), 0)
        # All results should have distance_km
        for f in data['features']:
            self.assertIn('distance_km', f['properties'])
            self.assertLessEqual(f['properties']['distance_km'], 5)

    def test_radius_sorted(self):
        resp = self.client.get('/api/spatial/radius?lat=43.65&lon=-79.38&radius_km=50')
        data = resp.get_json()
        dists = [f['properties']['distance_km'] for f in data['features']]
        self.assertEqual(dists, sorted(dists))

    def test_radius_excludes_far(self):
        # Vancouver should not appear in a Toronto radius query
        resp = self.client.get('/api/spatial/radius?lat=43.65&lon=-79.38&radius_km=100')
        data = resp.get_json()
        names = [f['properties']['name'] for f in data['features']]
        self.assertFalse(any('Vancouver' in n for n in names))

    def test_province_endpoint(self):
        resp = self.client.get('/api/spatial/province/ON')
        data = resp.get_json()
        self.assertIn('province_bounds', data)
        for f in data['features']:
            self.assertEqual(f['properties']['province'], 'ON')
