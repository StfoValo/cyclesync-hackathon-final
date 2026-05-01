let cachedSummaryData = null;
let cachedDemographicsData = null;
let riskChart, ageChart, genderChart, vehicleChart, behaviorChart, vehicleAgeChart;

let isInitialized = false;

export function initActuarial() {
    console.log("🚀 [Actuarial] initActuarial called. isInitialized:", isInitialized);

    if (isInitialized) {
        const regionalCharts = document.getElementById('regional-charts');
        if (regionalCharts && !regionalCharts.classList.contains('hidden')) {
            console.log("🔄 [Actuarial] Re-rendering Regional Charts from main tab switch.");
            loadRegionalCharts();
        } else {
            console.log("🔄 [Actuarial] Re-rendering Demographic Charts from main tab switch.");
            loadDemographics();
        }
        return;
    }

    const btnViewRegional = document.getElementById('btn-view-regional');
    const btnViewDemographic = document.getElementById('btn-view-demographic');
    const regionalCharts = document.getElementById('regional-charts');
    const demographicCharts = document.getElementById('demographic-charts');

    if (btnViewRegional && btnViewDemographic && regionalCharts && demographicCharts) {
        btnViewRegional.addEventListener('click', () => {
            console.log("🖱️ [Actuarial] 'Regional Overview' button clicked.");
            btnViewRegional.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.remove('text-slate-400', 'hover:text-white');

            btnViewDemographic.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.add('text-slate-400', 'hover:text-white');

            regionalCharts.classList.remove('hidden');
            demographicCharts.classList.add('hidden');
            loadRegionalCharts();
        });

        btnViewDemographic.addEventListener('click', () => {
            console.log("🖱️ [Actuarial] 'Demographic Deep Dive' button clicked.");
            btnViewDemographic.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.remove('text-slate-400', 'hover:text-white');

            btnViewRegional.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.add('text-slate-400', 'hover:text-white');

            demographicCharts.classList.remove('hidden');
            regionalCharts.classList.add('hidden');
            loadDemographics();
        });

        isInitialized = true;
        console.log("✅ [Actuarial] Event listeners attached. Loading initial Regional Charts.");
        loadRegionalCharts();
    } else {
        console.warn("⚠️ [Actuarial] Could not find DOM elements! Check your HTML IDs.");
    }
}

// ---------------------------------------------------------
// REGIONAL CHARTS LOGIC
// ---------------------------------------------------------
async function loadRegionalCharts() {
    console.log("📡 [Actuarial] loadRegionalCharts requested...");
    try {
        if (cachedSummaryData) {
            console.log("⚡ [Actuarial] Serving Regional data from JS cache.");
            renderRegionalCharts(cachedSummaryData);
            return;
        }

        console.log("🌐 [Actuarial] Fetching Regional data from API...");
        const res = await fetch('/api/actuarial/summary');
        if (!res.ok) throw new Error("HTTP error " + res.status);
        const data = await res.json();

        console.log("📦 [Actuarial] API Regional Data received:", data);
        cachedSummaryData = data;
        renderRegionalCharts(data);
    } catch (error) {
        console.error("❌ [Actuarial] Error loading regional charts:", error);
    }
}

function renderRegionalCharts(data) {
    console.log("🎨 [Actuarial] Rendering Regional Charts...");
    const kpis = data.kpis;
    document.getElementById('kpi-total-fleet').innerText = kpis.total_monitored_fleet.toLocaleString();
    document.getElementById('kpi-avg-premium').innerText = '€' + kpis.average_premium_eur.toLocaleString(undefined, { maximumFractionDigits: 0 });
    document.getElementById('kpi-discount').innerText = kpis.average_discount_pct.toLocaleString(undefined, { maximumFractionDigits: 1 }) + '%';
    document.getElementById('kpi-claims-reduction').innerText = kpis.claims_reduction_pct.toLocaleString(undefined, { maximumFractionDigits: 1 }) + '%';

    if (!riskChart) {
        console.log("🏗️ [Actuarial] Creating NEW riskChart instance.");
        const regions = data.regional_breakdown.map(r => r.region);
        const registered = data.regional_breakdown.map(r => r.registered_claims);
        const projected = data.regional_breakdown.map(r => r.projected_accidents);

        Chart.defaults.color = '#aaa';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

        riskChart = new Chart(document.getElementById('riskChart'), {
            type: 'bar',
            data: {
                labels: regions,
                datasets: [
                    { label: 'Registered Claims (Baseline)', data: registered, backgroundColor: 'rgba(120, 120, 120, 0.6)' },
                    { label: 'Projected Claims (Telematics)', data: projected, backgroundColor: 'rgba(226, 185, 59, 0.9)' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff' } },
                    datalabels: false // <-- Add this line
                },
                scales: {
                    y: { grid: { color: '#333' }, ticks: { color: '#aaa' } },
                    x: { grid: { display: false }, ticks: { color: '#aaa' } }
                }
            }
        });
    } else {
        console.log("♻️ [Actuarial] Updating EXISTING riskChart instance.");
        riskChart.update('none');
    }
}

// ---------------------------------------------------------
// DEMOGRAPHICS LOGIC
// ---------------------------------------------------------
async function loadDemographics() {
    console.log("📡 [Actuarial] loadDemographics requested...");
    try {
        if (cachedDemographicsData) {
            console.log("⚡ [Actuarial] Serving Demographics data from JS cache.");
            renderDemographics(cachedDemographicsData);
            return;
        }

        console.log("🌐 [Actuarial] Fetching Demographics data from API...");
        const res = await fetch('/api/actuarial/deep-dive');
        if (!res.ok) throw new Error("HTTP error " + res.status);
        const d = await res.json();

        console.log("📦 [Actuarial] API Demographics Data received:", d);
        cachedDemographicsData = d;
        renderDemographics(d);
    } catch (error) {
        console.error("❌ [Actuarial] Error loading demographics:", error);
    }
}

function renderDemographics(d) {
    console.log("🎨 [Actuarial] Rendering Demographics Charts...");
    Chart.defaults.color = '#aaa';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

    // 1. Add it to commonOptions
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            datalabels: false // <-- Add this here
        }
    };

    setTimeout(() => {
        if (!ageChart) {
            console.log("🏗️ [Actuarial] Creating NEW ageChart instance.");
            ageChart = new Chart(document.getElementById('ageChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.age_groups), datasets: [{ label: 'Projected Claims', data: Object.values(d.age_groups), backgroundColor: '#4CAF50' }] },
                options: commonOptions
            });
        } else {
            console.log("♻️ [Actuarial] Updating EXISTING ageChart instance.");
            ageChart.update('none');
        }

        if (!genderChart) {
            console.log("🏗️ [Actuarial] Creating NEW genderChart instance.");
            genderChart = new Chart(document.getElementById('genderChart'), {
                type: 'doughnut',
                data: { labels: Object.keys(d.genders), datasets: [{ data: Object.values(d.genders), backgroundColor: ['#2196F3', '#E91E63'], borderWidth: 0 }] },
                // 2. Add it to genderChart options
                options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { datalabels: false } }
            });
        } else {
            genderChart.update('none');
        }

        if (!vehicleChart) {
            console.log("🏗️ [Actuarial] Creating NEW vehicleChart instance.");
            vehicleChart = new Chart(document.getElementById('vehicleChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.vehicle_types), datasets: [{ label: 'Projected Claims', data: Object.values(d.vehicle_types), backgroundColor: '#FF9800' }] },
                // 3. Add it to vehicleChart options
                options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, datalabels: false } }
            });
        } else {
            vehicleChart.update('none');
        }

        if (!behaviorChart) {
            console.log("🏗️ [Actuarial] Creating NEW behaviorChart instance.");
            behaviorChart = new Chart(document.getElementById('behaviorChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.behaviors), datasets: [{ label: 'Projected Claims', data: Object.values(d.behaviors), backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'] }] },
                options: commonOptions
            });
        } else {
            behaviorChart.update('none');
        }

        if (!vehicleAgeChart) {
            console.log("🏗️ [Actuarial] Creating NEW vehicleAgeChart instance.");
            vehicleAgeChart = new Chart(document.getElementById('vehicleAgeChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.vehicle_ages), datasets: [{ label: 'Projected Claims', data: Object.values(d.vehicle_ages), backgroundColor: '#9C27B0' }] },
                options: commonOptions
            });
        } else {
            vehicleAgeChart.update('none');
        }
        console.log("✅ [Actuarial] All demographics charts rendered/updated.");
    }, 50); // 50ms delay
}