function openDetailPanel(id) {
  const feature = allFeatures.find(f => f.properties.id === id);
  if (!feature) return;
  const props = feature.properties;
  const [lon, lat] = feature.geometry.coordinates;

  const size = props.size_category || 'colocation';
  const sizeLabel = size.charAt(0).toUpperCase() + size.slice(1);
  const certs = props.certifications ? props.certifications.split(',').map(c => `<span class="cert-tag">${c.trim()}</span>`).join('') : '';

  const rows = [
    ['Operator', props.operator],
    ['City', props.city],
    ['Province', props.province_full || props.province],
    ['Size', `<span class="popup-badge badge-${size}">${sizeLabel}</span>`],
    ['Power Capacity', props.power_mw ? `${props.power_mw} MW` : 'N/A'],
    ['Floor Space', props.floor_space_sqft ? `${props.floor_space_sqft.toLocaleString()} sq ft` : 'N/A'],
    ['Established', props.year_established || 'N/A'],
    ['Tier Rating', props.tier_rating ? `Tier ${props.tier_rating}` : 'N/A'],
    ['Address', props.address || 'N/A'],
  ].map(([k, v]) => `
    <div class="detail-row">
      <span class="detail-key">${k}</span>
      <span class="detail-value">${v}</span>
    </div>
  `).join('');

  const websiteLink = props.operator_url
    ? `<a href="${props.operator_url}" target="_blank" rel="noopener" class="detail-link">Visit operator website ↗</a>`
    : '';

  document.getElementById('detail-content').innerHTML = `
    <div class="detail-name">${props.name}</div>
    <div class="detail-operator">${props.operator}</div>
    ${rows}
    ${certs ? `<div class="detail-certs">${certs}</div>` : ''}
    ${websiteLink}
    <div class="nearest-section">
      <div class="nearest-title">Nearest Data Centres (50 km)</div>
      <div id="nearest-list"><em style="color:#8892a4;font-size:12px;">Loading...</em></div>
    </div>
  `;

  document.getElementById('detail-panel').classList.add('open');
  document.getElementById('stats-panel').classList.remove('open');

  // Pan map to marker
  map.panTo([lat, lon]);

  // Load nearest DCs
  fetch(`/api/spatial/radius?lat=${lat}&lon=${lon}&radius_km=50`)
    .then(r => r.json())
    .then(data => {
      const others = (data.features || []).filter(f => f.properties.id !== id).slice(0, 5);
      const list = document.getElementById('nearest-list');
      if (!list) return;
      if (others.length === 0) {
        list.innerHTML = '<em style="color:#8892a4;font-size:12px;">None within 50 km</em>';
        return;
      }
      list.innerHTML = others.map(f => `
        <div class="nearest-item" onclick="openDetailPanel(${f.properties.id})">
          <span class="nearest-name">${f.properties.name}</span>
          <span class="nearest-dist">${f.properties.distance_km} km</span>
        </div>
      `).join('');
    })
    .catch(() => {
      const list = document.getElementById('nearest-list');
      if (list) list.innerHTML = '<em style="color:#8892a4;font-size:12px;">Unable to load</em>';
    });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('detail-close').addEventListener('click', () => {
    document.getElementById('detail-panel').classList.remove('open');
  });
  document.getElementById('stats-close').addEventListener('click', () => {
    document.getElementById('stats-panel').classList.remove('open');
  });
  document.getElementById('stats-btn').addEventListener('click', () => {
    document.getElementById('stats-panel').classList.toggle('open');
    document.getElementById('detail-panel').classList.remove('open');
  });
});
