from flask import Blueprint, jsonify
from database.db import get_db

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/api/stats/summary')
def summary():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM data_centres").fetchone()[0]

    by_province = {}
    for row in db.execute("SELECT province, COUNT(*) as cnt FROM data_centres GROUP BY province ORDER BY cnt DESC"):
        by_province[row['province']] = row['cnt']

    by_size = {}
    for row in db.execute("SELECT size_category, COUNT(*) as cnt FROM data_centres GROUP BY size_category ORDER BY cnt DESC"):
        by_size[row['size_category']] = row['cnt']

    by_operator = {}
    for row in db.execute("SELECT operator, COUNT(*) as cnt FROM data_centres GROUP BY operator ORDER BY cnt DESC LIMIT 10"):
        by_operator[row['operator']] = row['cnt']

    by_decade = {}
    for row in db.execute("SELECT year_established FROM data_centres WHERE year_established IS NOT NULL"):
        decade = f"{(row['year_established'] // 10) * 10}s"
        by_decade[decade] = by_decade.get(decade, 0) + 1

    return jsonify({
        "total_dcs": total,
        "by_province": by_province,
        "by_size": by_size,
        "by_operator": by_operator,
        "by_decade": dict(sorted(by_decade.items())),
    })


@stats_bp.route('/api/stats/operators')
def operators():
    db = get_db()
    rows = db.execute("SELECT DISTINCT operator FROM data_centres ORDER BY operator").fetchall()
    return jsonify([r['operator'] for r in rows])


@stats_bp.route('/api/stats/provinces')
def provinces():
    db = get_db()
    rows = db.execute(
        "SELECT province, province_full, COUNT(*) as dc_count FROM data_centres GROUP BY province ORDER BY dc_count DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])
