import sqlite3
import os
from flask import g
import config


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(config.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(config.DATABASE), exist_ok=True)
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    from database.seed import seed_data
    seed_data(conn)
    conn.close()
