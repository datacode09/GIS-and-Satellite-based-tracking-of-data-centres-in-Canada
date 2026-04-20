const SIZE_COLOURS = {
  hyperscale: '#ef4444',
  enterprise:  '#f97316',
  colocation:  '#3b82f6',
  edge:        '#22c55e',
};

let allFeatures = [];

function makeIcon(size) {
  const colour = SIZE_COLOURS[size] || '#8892a4';
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18">
    <circle cx="9" cy="9" r="7" fill="${colour}" stroke="#fff" stroke-width="2"/>
  </svg>`;
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    popupAnchor: [0, -12],
  });
}

function buildPopupHTML(props) {
  const size = props.size_category || 'colocation';
  const sizeLabel = size.charAt(0).toUpperCase() + size.slice(1);
  const power = props.power_mw ? `${props.power_mw} MW` : 'N/A';
  return `
    <div class="popup-name">${props.name}</div>
    <div class="popup-sub">${props.city}, ${props.province_full || props.province}</div>
    <span class="popup-badge badge-${size}">${sizeLabel}</span>
    <div style="font-size:12px;color:#8892a4;margin-bottom:4px;">
      ${props.operator} &bull; ${props.year_established || 'N/A'} &bull; ${power}
    </div>
    <button class="popup-detail-btn" onclick="openDetailPanel(${props.id})">More details</button>
  `;
}

function renderFeatures(features) {
  allFeatures = features;
  clusterLayer.clearLayers();

  const heatPoints = [];

  features.forEach(f => {
    const props = f.properties;
    const [lon, lat] = f.geometry.coordinates;
    const marker = L.marker([lat, lon], { icon: makeIcon(props.size_category) });
    marker.bindPopup(buildPopupHTML(props), { maxWidth: 220 });
    marker.bindTooltip(props.name, { direction: 'top', offset: [0, -12] });
    marker.featureData = f;
    clusterLayer.addLayer(marker);

    const weight = props.power_mw ? Math.min(props.power_mw / 30, 1.0) : 0.3;
    heatPoints.push([lat, lon, weight]);
  });

  heatLayer.setLatLngs(heatPoints);

  const total = document.getElementById('stat-total');
  if (total) total.textContent = features.length;
}

async function fetchAndRender(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const url = `/api/datacentres/geojson${qs ? '?' + qs : ''}`;
  try {
    const resp = await fetch(url);
    const data = await resp.json();
    renderFeatures(data.features || []);
    updateStatus(data.features ? data.features.length : 0);
    return data.features || [];
  } catch (e) {
    console.error('Failed to fetch data centres:', e);
    updateStatus(0, true);
    return [];
  }
}

function updateStatus(count, error = false) {
  const el = document.getElementById('status-text');
  if (!el) return;
  if (error) { el.textContent = 'Error loading data.'; return; }
  const total = allFeatures.length || count;
  el.textContent = `Showing ${count} of ${total >= count ? total : count} data centres`;
}

// Initial load
document.addEventListener('DOMContentLoaded', () => fetchAndRender());
