let tiresChart, brakesChart, batteriesChart;
let cachedEsgData = null;

export function initESG() {
    loadESGDashboard();
}

async function loadESGDashboard() {
    try {
        // If we already have the data, render it instantly and stop!
        if (cachedEsgData) {
            renderESG(cachedEsgData);
            return;
        }

        // Temporary Loading UX
        document.getElementById('esg-kpi-baseline').innerText = 'Loading...';
        document.getElementById('esg-kpi-real').innerText = 'Loading...';
        document.getElementById('esg-kpi-saved').innerText = 'Loading...';
        document.getElementById('esg-kpi-trees').innerText = 'Loading...';

        const res = await fetch('/api/actuarial/esg');
        if (!res.ok) throw new Error("HTTP error " + res.status);
        const data = await res.json();

        // Save to cache, then render
        cachedEsgData = data;
        renderESG(data);

    } catch (error) {
        console.error("Failed to load ESG dashboard:", error);
        document.getElementById('esg-kpi-baseline').innerText = 'Error';
    }
}

function renderESG(data) {
    const emissions = data.emissions;
    const circular = data.circular_economy;

    // KPIs
    document.getElementById('esg-kpi-baseline').innerText = emissions.baseline_co2_tons.toLocaleString(undefined, { maximumFractionDigits: 0 });
    document.getElementById('esg-kpi-real').innerText = emissions.real_telematics_co2_tons.toLocaleString(undefined, { maximumFractionDigits: 0 });
    document.getElementById('esg-kpi-saved').innerText = emissions.co2_saved_tons.toLocaleString(undefined, { maximumFractionDigits: 0 });
    document.getElementById('esg-kpi-trees').innerText = emissions.equivalent_trees_planted.toLocaleString();

    document.getElementById('esg-kpi-tires-total').innerText = circular.recovered_tires.total_units.toLocaleString() + ' Units';
    document.getElementById('esg-kpi-brakes-total').innerText = circular.recovered_brakes.total_units.toLocaleString() + ' Units';
    document.getElementById('esg-kpi-batteries-total').innerText = circular.recovered_ev_batteries.total_units.toLocaleString() + ' Units';

    // Charts Colors & Options
    const ecoColors1 = ['#059669', '#10b981', '#34d399'];
    const ecoColors2 = ['#d97706', '#f59e0b', '#fbbf24'];
    const ecoColors3 = ['#2563eb', '#3b82f6', '#60a5fa'];

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { color: '#cbd5e1', padding: 20 } },
        }
    };

    // Tires
    const tiresData = circular.recovered_tires.destinations;
    if (tiresChart) tiresChart.destroy();
    tiresChart = new window.Chart(document.getElementById('esgTiresChart'), {
        type: 'doughnut',
        data: { labels: Object.keys(tiresData).map(k => k.replace(/_/g, ' ')), datasets: [{ data: Object.values(tiresData), backgroundColor: ecoColors1, borderWidth: 0 }] },
        options: chartOptions
    });

    // Brakes
    const brakesData = circular.recovered_brakes.destinations;
    if (brakesChart) brakesChart.destroy();
    brakesChart = new window.Chart(document.getElementById('esgBrakesChart'), {
        type: 'doughnut',
        data: { labels: Object.keys(brakesData).map(k => k.replace(/_/g, ' ')), datasets: [{ data: Object.values(brakesData), backgroundColor: ecoColors2, borderWidth: 0 }] },
        options: chartOptions
    });

    // Batteries
    const batteriesData = circular.recovered_ev_batteries.destinations;
    if (batteriesChart) batteriesChart.destroy();
    batteriesChart = new window.Chart(document.getElementById('esgBatteriesChart'), {
        type: 'doughnut',
        data: { labels: Object.keys(batteriesData).map(k => k.replace(/_/g, ' ')), datasets: [{ data: Object.values(batteriesData), backgroundColor: ecoColors3, borderWidth: 0 }] },
        options: chartOptions
    });
}