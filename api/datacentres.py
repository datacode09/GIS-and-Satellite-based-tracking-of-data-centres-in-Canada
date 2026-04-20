from flask import Blueprint, jsonify, request
from database.db import get_db

datacentres_bp = Blueprint('datacentres', __name__)


def row_to_feature(row):
    props = dict(row)
    lat = props.pop('latitude')
    lon = props.pop('longitude')
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": props,
    }


def build_filter_query(args):
    conditions = []
    params = []

    province = args.get('province', '').strip().upper()
    if province:
        placeholders = ','.join('?' for p in province.split(','))
        conditions.append(f"province IN ({placeholders})")
        params.extend(province.split(','))

    size = args.get('size', '').strip().lower()
    if size:
        placeholders = ','.join('?' for s in size.split(','))
        conditions.append(f"size_category IN ({placeholders})")
        params.extend(size.split(','))

    operator = args.get('operator', '').strip()
    if operator:
        conditions.append("LOWER(operator) LIKE ?")
        params.append(f"%{operator.lower()}%")

    year_min = args.get('year_min', '').strip()
    if year_min and year_min.isdigit():
        conditions.append("year_established >= ?")
        params.append(int(year_min))

    year_max = args.get('year_max', '').strip()
    if year_max and year_max.isdigit():
        conditions.append("year_established <= ?")
        params.append(int(year_max))

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
    return where, params


@datacentres_bp.route('/api/datacentres/geojson')
def geojson():
    where, params = build_filter_query(request.args)
    db = get_db()
    rows = db.execute(f"SELECT * FROM data_centres {where} ORDER BY name", params).fetchall()
    features = [row_to_feature(r) for r in rows]
    return jsonify({"type": "FeatureCollection", "features": features})


@datacentres_bp.route('/api/datacentres')
def list_datacentres():
    where, params = build_filter_query(request.args)
    db = get_db()
    rows = db.execute(f"SELECT * FROM data_centres {where} ORDER BY name", params).fetchall()
    total = db.execute("SELECT COUNT(*) FROM data_centres").fetchone()[0]
    return jsonify({"total": total, "count": len(rows), "results": [dict(r) for r in rows]})


@datacentres_bp.route('/api/datacentres/<int:dc_id>')
def get_datacentre(dc_id):
    db = get_db()
    row = db.execute("SELECT * FROM data_centres WHERE id = ?", (dc_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Not found", "status": 404}), 404
    return jsonify(row_to_feature(row))
