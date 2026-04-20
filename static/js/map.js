// Global map instance and layer references shared across modules
let map, clusterLayer, heatLayer;

(function initMap() {
  map = L.map('map', {
    center: [56.0, -96.0],
    zoom: 4,
    minZoom: 3,
    maxZoom: 19,
  });

  const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  });

  const esriSatellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
      maxZoom: 19,
    }
  );

  esriSatellite.on('tileerror', () => {
    if (map.hasLayer(esriSatellite)) {
      map.removeLayer(esriSatellite);
      osm.addTo(map);
    }
  });

  const esriTopo = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    {
      attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
      maxZoom: 19,
    }
  );

  const cartoDark = L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }
  );

  const cartoLight = L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }
  );

  osm.addTo(map);

  clusterLayer = L.markerClusterGroup({ chunkedLoading: true, maxClusterRadius: 60 });
  clusterLayer.addTo(map);

  heatLayer = L.heatLayer([], { radius: 35, blur: 25, maxZoom: 10, minOpacity: 0.4 });

  L.control.layers(
    {
      'Street (OpenStreetMap)': osm,
      'Satellite (Esri World Imagery)': esriSatellite,
      'Topographic (Esri)': esriTopo,
      'Dark (CartoDB)': cartoDark,
      'Light (CartoDB)': cartoLight,
    },
    {
      'Data Centres': clusterLayer,
      'Heat Map': heatLayer,
    },
    { position: 'topright', collapsed: true }
  ).addTo(map);

  // Fit Canada button
  const fitControl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd() {
      const btn = L.DomUtil.create('button', 'leaflet-bar leaflet-control');
      btn.title = 'Fit Canada';
      btn.style.cssText = 'background:#1a1d27;color:#e2e8f0;border:1px solid #2e3248;padding:5px 8px;cursor:pointer;font-size:11px;font-weight:600;';
      btn.textContent = 'CA';
      L.DomEvent.on(btn, 'click', () => map.setView([56.0, -96.0], 4));
      return btn;
    },
  });
  new fitControl().addTo(map);
})();
