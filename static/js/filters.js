let filterState = {
  provinces: [],
  sizes: ['hyperscale', 'enterprise', 'colocation', 'edge'],
  operator: '',
  yearMin: 1990,
  yearMax: 2030,
};

async function populateFilterDropdowns() {
  try {
    const [opsResp, provResp] = await Promise.all([
      fetch('/api/stats/operators'),
      fetch('/api/stats/provinces'),
    ]);
    const operators = await opsResp.json();
    const provinces = await provResp.json();

    const opSelect = document.getElementById('operator-filter');
    operators.forEach(op => {
      const opt = document.createElement('option');
      opt.value = op;
      opt.textContent = op;
      opSelect.appendChild(opt);
    });

    const provContainer = document.getElementById('province-filters');
    provinces.forEach(p => {
      const label = document.createElement('label');
      label.className = 'filter-label';
      label.innerHTML = `
        <input type="checkbox" class="province-filter" value="${p.province}" checked />
        ${p.province_full} <span style="color:#8892a4;font-size:11px;">(${p.dc_count})</span>
      `;
      provContainer.appendChild(label);
    });
  } catch (e) {
    console.error('Failed to load filter options:', e);
  }
}

function readFilterState() {
  const provinces = [...document.querySelectorAll('.province-filter:checked')].map(el => el.value);
  const sizes = [...document.querySelectorAll('.size-filter:checked')].map(el => el.value);
  const operator = document.getElementById('operator-filter').value;
  const yearMin = parseInt(document.getElementById('year-min').value) || 1990;
  const yearMax = parseInt(document.getElementById('year-max').value) || 2030;
  filterState = { provinces, sizes, operator, yearMin, yearMax };
}

function buildQueryParams() {
  const p = {};
  if (filterState.provinces.length > 0) p.province = filterState.provinces.join(',');
  if (filterState.sizes.length > 0 && filterState.sizes.length < 4) p.size = filterState.sizes.join(',');
  if (filterState.operator) p.operator = filterState.operator;
  if (filterState.yearMin > 1990) p.year_min = filterState.yearMin;
  if (filterState.yearMax < 2030) p.year_max = filterState.yearMax;
  return p;
}

async function applyFilters() {
  readFilterState();
  const features = await fetchAndRender(buildQueryParams());
  const el = document.getElementById('status-text');
  if (el) el.textContent = `Showing ${features.length} data centres`;
}

function resetFilters() {
  document.querySelectorAll('.province-filter').forEach(el => { el.checked = true; });
  document.querySelectorAll('.size-filter').forEach(el => { el.checked = true; });
  document.getElementById('operator-filter').value = '';
  document.getElementById('year-min').value = 1990;
  document.getElementById('year-max').value = 2030;
  fetchAndRender();
}

// Search
function setupSearch() {
  const input = document.getElementById('search-input');
  if (!input) return;
  input.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();
    if (!query) { renderFeatures(allFeatures); updateStatus(allFeatures.length); return; }
    const filtered = allFeatures.filter(f => {
      const p = f.properties;
      return (
        (p.name || '').toLowerCase().includes(query) ||
        (p.operator || '').toLowerCase().includes(query) ||
        (p.city || '').toLowerCase().includes(query) ||
        (p.province_full || '').toLowerCase().includes(query)
      );
    });
    renderFeatures(filtered);
    updateStatus(filtered.length);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  populateFilterDropdowns();
  setupSearch();
  document.getElementById('apply-filters').addEventListener('click', applyFilters);
  document.getElementById('reset-filters').addEventListener('click', resetFilters);
});
