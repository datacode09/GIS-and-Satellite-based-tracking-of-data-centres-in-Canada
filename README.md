# Canadian Data Centre GIS Tracker

An interactive GIS and satellite-based web tool for tracking data centres across Canada. Built with Python/Flask, Leaflet.js, and free satellite imagery (no API keys required).

## Features

- **Interactive map** of 35 real Canadian data centres across 8 provinces
- **Satellite imagery** via Esri World Imagery (free, no API key)
- **5 base layers**: Street (OSM), Satellite (Esri), Topographic, CartoDB Light, CartoDB Dark
- **Marker clustering** for dense urban areas (Toronto, Montreal, Vancouver)
- **Heatmap overlay** weighted by power capacity (MW)
- **Filter panel**: by province, size category, operator, year range
- **Search** by name, operator, or city (real-time)
- **Detail panel** with full data centre info + nearest DCs within 50 km
- **Statistics panel** with Chart.js visualisations (province, size, decade)
- **REST API** with GeoJSON, bounding box, and radius spatial queries

## Quick Start

```bash
git clone <repo>
cd GIS-and-Satellite-based-tracking-of-data-centres-in-Canada
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000**

## API Reference

```bash
# All data centres (GeoJSON)
curl http://localhost:5000/api/datacentres/geojson

# Filter by province
curl "http://localhost:5000/api/datacentres/geojson?province=ON"

# Filter by size and operator
curl "http://localhost:5000/api/datacentres/geojson?size=hyperscale&operator=aws"

# Spatial radius query (50 km from downtown Toronto)
curl "http://localhost:5000/api/spatial/radius?lat=43.65&lon=-79.38&radius_km=50"

# Bounding box query
curl "http://localhost:5000/api/spatial/bbox?north=44&south=43.5&east=-79&west=-80"

# All Ontario data centres + province bounds
curl http://localhost:5000/api/spatial/province/ON

# Statistics summary
curl http://localhost:5000/api/stats/summary

# Health check
curl http://localhost:5000/api/health
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Data Centres Included

| Province | Count | Key Operators |
|----------|-------|---------------|
| Ontario | 14 | Equinix (5), Cologix (2), Microsoft, Amazon |
| Quebec | 9 | Cologix, Equinix, AWS, Google, QScale |
| British Columbia | 5 | Equinix, Cologix, Telus, Shaw |
| Alberta | 5 | Cologix, Shaw, Telus |
| Manitoba | 1 | Bell MTS |
| Nova Scotia | 1 | Bell |
| Saskatchewan | 1 | SaskTel |

## Size Categories

| Category | Description | Colour |
|----------|-------------|--------|
| Hyperscale | Cloud giants (AWS, Azure, Google, QScale) | Red |
| Enterprise | Telco-owned, large private | Orange |
| Colocation | Carrier-neutral colo facilities | Blue |
| Edge | Regional / smaller facilities | Green |

## Architecture

```
app.py              Flask entry point
config.py           Configuration
database/
  schema.sql        SQLite schema
  seed.py           35-record curated dataset
  db.py             Connection management
api/
  datacentres.py    /api/datacentres/* endpoints
  spatial.py        /api/spatial/* (bbox, radius, province)
  stats.py          /api/stats/* (summary, operators, provinces)
static/
  css/style.css     Dark theme layout
  js/map.js         Leaflet map + tile layers
  js/markers.js     Cluster markers + popups
  js/filters.js     Filter panel logic
  js/sidebar.js     Detail + stats panels
  js/charts.js      Chart.js statistics
templates/
  index.html        Single-page application
tests/              28 unit tests
```

## Data Sources

Operator websites, press releases, and public infrastructure registries including:
- Equinix, Cologix, DataBank facility pages
- AWS, Azure, Google Cloud region announcements
- Statistics Canada open data
- DatacenterMap.com public listings

Coordinates are approximate (city/district level) for publicly known facilities.
