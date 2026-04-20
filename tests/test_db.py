import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
import tempfile
import unittest
import config


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self._orig_db = config.DATABASE
        config.DATABASE = self.db_path

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        with open(schema_path) as f:
            conn.executescript(f.read())
        from database.seed import seed_data
        seed_data(conn)
        conn.close()

    def tearDown(self):
        config.DATABASE = self._orig_db
        os.unlink(self.db_path)

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def test_seed_count(self):
        conn = self._conn()
        count = conn.execute("SELECT COUNT(*) FROM data_centres").fetchone()[0]
        conn.close()
        self.assertGreater(count, 30)

    def test_no_null_coordinates(self):
        conn = self._conn()
        nulls = conn.execute(
            "SELECT COUNT(*) FROM data_centres WHERE latitude IS NULL OR longitude IS NULL"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(nulls, 0)

    def test_no_null_names(self):
        conn = self._conn()
        nulls = conn.execute(
            "SELECT COUNT(*) FROM data_centres WHERE name IS NULL OR operator IS NULL"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(nulls, 0)

    def test_size_category_constraint(self):
        conn = self._conn()
        invalid = conn.execute(
            "SELECT COUNT(*) FROM data_centres WHERE size_category NOT IN ('hyperscale','enterprise','colocation','edge')"
        ).fetchone()[0]
        conn.close()
        self.assertEqual(invalid, 0)

    def test_idempotent_seed(self):
        conn = self._conn()
        before = conn.execute("SELECT COUNT(*) FROM data_centres").fetchone()[0]
        from database.seed import seed_data
        seed_data(conn)
        after = conn.execute("SELECT COUNT(*) FROM data_centres").fetchone()[0]
        conn.close()
        self.assertEqual(before, after)
