import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile
import unittest
import config


class TestDatacentresAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        config.DATABASE = self.tmp.name
        self.tmp.close()
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(config.DATABASE)

    def test_geojson_all(self):
        resp = self.client.get('/api/datacentres/geojson')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['type'], 'FeatureCollection')
        self.assertGreater(len(data['features']), 30)

    def test_geojson_feature_structure(self):
        resp = self.client.get('/api/datacentres/geojson')
        data = resp.get_json()
        f = data['features'][0]
        self.assertEqual(f['type'], 'Feature')
        self.assertEqual(f['geometry']['type'], 'Point')
        self.assertEqual(len(f['geometry']['coordinates']), 2)
        self.assertIn('name', f['properties'])
        self.assertIn('operator', f['properties'])

    def test_geojson_coordinate_order(self):
        resp = self.client.get('/api/datacentres/geojson')
        data = resp.get_json()
        for f in data['features']:
            lon, lat = f['geometry']['coordinates']
            # Canada longitude is negative (west), latitude is positive
            self.assertLess(lon, 0, "Longitude should be negative for Canada")
            self.assertGreater(lat, 40, "Latitude should be > 40 for Canada")

    def test_filter_by_province(self):
        resp = self.client.get('/api/datacentres/geojson?province=ON')
        data = resp.get_json()
        for f in data['features']:
            self.assertEqual(f['properties']['province'], 'ON')

    def test_filter_by_size(self):
        resp = self.client.get('/api/datacentres/geojson?size=hyperscale')
        data = resp.get_json()
        for f in data['features']:
            self.assertEqual(f['properties']['size_category'], 'hyperscale')

    def test_filter_nonexistent_province(self):
        resp = self.client.get('/api/datacentres/geojson?province=ZZ')
        data = resp.get_json()
        self.assertEqual(data['features'], [])

    def test_get_by_id(self):
        resp = self.client.get('/api/datacentres/1')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['properties']['id'], 1)

    def test_get_by_id_404(self):
        resp = self.client.get('/api/datacentres/99999')
        self.assertEqual(resp.status_code, 404)

    def test_list_endpoint(self):
        resp = self.client.get('/api/datacentres')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('total', data)
        self.assertIn('results', data)
