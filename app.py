import os
import sqlite3
from flask import Flask, render_template, jsonify
from flask_cors import CORS

import config
from database.db import init_db, close_db, get_db
from api.datacentres import datacentres_bp
from api.spatial import spatial_bp
from api.stats import stats_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    app.teardown_appcontext(close_db)

    app.register_blueprint(datacentres_bp)
    app.register_blueprint(spatial_bp)
    app.register_blueprint(stats_bp)

    with app.app_context():
        init_db()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health():
        db = get_db()
        dc_count = db.execute("SELECT COUNT(*) FROM data_centres").fetchone()[0]
        db_size_kb = round(os.path.getsize(config.DATABASE) / 1024, 1) if os.path.exists(config.DATABASE) else 0
        return jsonify({"status": "ok", "dc_count": dc_count, "db_size_kb": db_size_kb})

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=5000, host='0.0.0.0')
