import math
from flask import Blueprint, jsonify, request
from database.db import get_db

spatial_bp = Blueprint('spatial', __name__)

PROVINCE_BOUNDS = {
    'BC':  [[48.3, -139.1], [60.0, -114.0]],
    'AB':  [[49.0, -120.0], [60.0, -110.0]],
    'SK':  [[49.0, -110.0], [60.0, -101.4]],
    'MB':  [[49.0, -102.0], [60.0,  -88.9]],
    'ON':  [[41.6,  -95.2], [56.9,  -74.3]],
    'QC':  [[44.9,  -79.8], [62.6,  -57.1]],
    'NB':  [[44.5,  -67.8], [48.1,  -63.8]],
    'NS':  [[43.3,  -66.3], [47.1,  -59.7]],
    'PE':  [[45.9,  -64.4], [47.1,  -61.9]],
    'NL':  [[46.6,  -67.8], [60.4,  -52.6]],
    'YT':  [[59.8, -141.0], [69.7, -123.8]],
    'NT':  [[59.8, -136.5], [78.6, -101.4]],
    'NU':  [[61.5, -120.7], [83.1,  -61.2]],
}


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def row_to_feature(row, extra_props=None):
    props = dict(row)
    lat = props.pop('latitude')
    lon = props.pop('longitude')
    if extra_props:
        props.update(extra_props)
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": props,
    }


@spatial_bp.route('/api/spatial/bbox')
def bbox():
    try:
        north = float(request.args['north'])
        south = float(request.args['south'])
        east = float(request.args['east'])
        west = float(request.args['west'])
    except (KeyError, ValueError):
        return jsonify({"error": "Required: north, south, east, west (floats)", "status": 400}), 400

    db = get_db()
    rows = db.execute(
        "SELECT * FROM data_centres WHERE latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?",
        (south, north, west, east),
    ).fetchall()
    features = [row_to_feature(r) for r in rows]
    return jsonify({"type": "FeatureCollection", "features": features})


@spatial_bp.route('/api/spatial/radius')
def radius():
    try:
        lat = float(request.args['lat'])
        lon = float(request.args['lon'])
        radius_km = float(request.args.get('radius_km', 50))
    except (KeyError, ValueError):
        return jsonify({"error": "Required: lat, lon (floats). Optional: radius_km", "status": 400}), 400

    db = get_db()
    rows = db.execute("SELECT * FROM data_centres").fetchall()
    results = []
    for row in rows:
        d = haversine_km(lat, lon, row['latitude'], row['longitude'])
        if d <= radius_km:
            results.append(row_to_feature(row, {"distance_km": round(d, 2)}))
    results.sort(key=lambda f: f['properties']['distance_km'])
    return jsonify({"type": "FeatureCollection", "features": results})


@spatial_bp.route('/api/spatial/province/<province_code>')
def province(province_code):
    code = province_code.upper()
    db = get_db()
    rows = db.execute("SELECT * FROM data_centres WHERE province = ?", (code,)).fetchall()
    features = [row_to_feature(r) for r in rows]
    bounds = PROVINCE_BOUNDS.get(code)
    return jsonify({
        "type": "FeatureCollection",
        "features": features,
        "province_bounds": bounds,
    })
