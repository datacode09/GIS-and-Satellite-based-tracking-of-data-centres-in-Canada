Chart.defaults.color = '#8892a4';
Chart.defaults.borderColor = '#2e3248';

async function loadStats() {
  try {
    const resp = await fetch('/api/stats/summary');
    const data = await resp.json();

    document.getElementById('stat-total').textContent = data.total_dcs;

    const colours = {
      hyperscale: '#ef4444',
      enterprise:  '#f97316',
      colocation:  '#3b82f6',
      edge:        '#22c55e',
    };

    // Province chart
    const provLabels = Object.keys(data.by_province);
    const provCounts = Object.values(data.by_province);
    new Chart(document.getElementById('chart-province'), {
      type: 'bar',
      data: {
        labels: provLabels,
        datasets: [{
          label: 'Data Centres',
          data: provCounts,
          backgroundColor: '#3b82f6',
          borderRadius: 4,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#2e3248' }, ticks: { font: { size: 11 } } },
          y: { grid: { color: '#2e3248' }, ticks: { stepSize: 1, font: { size: 11 } }, beginAtZero: true },
        },
      },
    });

    // Size doughnut
    const sizeLabels = Object.keys(data.by_size).map(s => s.charAt(0).toUpperCase() + s.slice(1));
    const sizeCounts = Object.values(data.by_size);
    const sizeBg = Object.keys(data.by_size).map(s => colours[s] || '#8892a4');
    new Chart(document.getElementById('chart-size'), {
      type: 'doughnut',
      data: {
        labels: sizeLabels,
        datasets: [{ data: sizeCounts, backgroundColor: sizeBg, borderWidth: 2, borderColor: '#1a1d27' }],
      },
      options: {
        plugins: {
          legend: { position: 'right', labels: { font: { size: 11 }, padding: 10 } },
        },
        cutout: '60%',
      },
    });

    // Decade chart
    const decadeLabels = Object.keys(data.by_decade);
    const decadeCounts = Object.values(data.by_decade);
    new Chart(document.getElementById('chart-decade'), {
      type: 'bar',
      data: {
        labels: decadeLabels,
        datasets: [{
          label: 'Data Centres',
          data: decadeCounts,
          backgroundColor: '#22c55e',
          borderRadius: 4,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#2e3248' }, ticks: { font: { size: 11 } } },
          y: { grid: { color: '#2e3248' }, ticks: { stepSize: 1, font: { size: 11 } }, beginAtZero: true },
        },
      },
    });
  } catch (e) {
    console.error('Failed to load stats:', e);
  }
}

document.addEventListener('DOMContentLoaded', loadStats);
