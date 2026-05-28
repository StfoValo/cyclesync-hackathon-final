import { initPredictiveAsset } from './predictive_asset.js';

let cachedSummaryData = null;
let cachedDemographicsData = null;
let riskChart, ageChart, genderChart, vehicleChart, behaviorChart, vehicleAgeChart;

let isInitialized = false;

let activeSubView = 'regional'; // can be 'regional', 'demographic', 'asset'

export function initActuarial() {
    console.log("🚀 [Actuarial] initActuarial called. isInitialized:", isInitialized);

    if (isInitialized) {
        if (activeSubView === 'regional') {
            console.log("🔄 [Actuarial] Re-rendering Regional Charts from main tab switch.");
            loadRegionalCharts();
        } else if (activeSubView === 'demographic') {
            console.log("🔄 [Actuarial] Re-rendering Demographic Charts from main tab switch.");
            loadDemographics();
        } else if (activeSubView === 'asset') {
            console.log("🔄 [Actuarial] Re-rendering Asset Charts from main tab switch.");
            initPredictiveAsset();
        }
        return;
    }

    const btnViewRegional = document.getElementById('btn-view-regional');
    const btnViewDemographic = document.getElementById('btn-view-demographic');
    const btnViewAsset = document.getElementById('btn-view-asset');

    const regionalCharts = document.getElementById('regional-charts');
    const demographicCharts = document.getElementById('demographic-charts');
    const executiveContentWrapper = document.getElementById('executive-content-wrapper');
    const assetContentWrapper = document.getElementById('asset-content-wrapper');

    if (btnViewRegional && btnViewDemographic && btnViewAsset && regionalCharts && demographicCharts && executiveContentWrapper && assetContentWrapper) {
        btnViewRegional.addEventListener('click', () => {
            console.log("🖱️ [Actuarial] 'Regional Overview' button clicked.");
            activeSubView = 'regional';

            btnViewRegional.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.remove('text-slate-400', 'hover:text-white');

            btnViewDemographic.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.add('text-slate-400', 'hover:text-white');

            btnViewAsset.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewAsset.classList.add('text-slate-400', 'hover:text-white');

            executiveContentWrapper.classList.remove('hidden');
            assetContentWrapper.classList.add('hidden');

            regionalCharts.classList.remove('hidden');
            demographicCharts.classList.add('hidden');
            loadRegionalCharts();
        });

        btnViewDemographic.addEventListener('click', () => {
            console.log("🖱️ [Actuarial] 'Demographic Deep Dive' button clicked.");
            activeSubView = 'demographic';

            btnViewDemographic.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.remove('text-slate-400', 'hover:text-white');

            btnViewRegional.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.add('text-slate-400', 'hover:text-white');

            btnViewAsset.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewAsset.classList.add('text-slate-400', 'hover:text-white');

            executiveContentWrapper.classList.remove('hidden');
            assetContentWrapper.classList.add('hidden');

            demographicCharts.classList.remove('hidden');
            regionalCharts.classList.add('hidden');
            loadDemographics();
        });

        btnViewAsset.addEventListener('click', () => {
            console.log("🖱️ [Actuarial] 'Asset Risk' button clicked.");
            activeSubView = 'asset';

            btnViewAsset.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewAsset.classList.remove('text-slate-400', 'hover:text-white');

            btnViewRegional.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.add('text-slate-400', 'hover:text-white');

            btnViewDemographic.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.add('text-slate-400', 'hover:text-white');

            executiveContentWrapper.classList.add('hidden');
            assetContentWrapper.classList.remove('hidden');

            initPredictiveAsset();
        });

        isInitialized = true;
        console.log("✅ [Actuarial] Event listeners attached. Loading initial Regional Charts.");
        loadRegionalCharts();
    } else {
        console.warn("⚠️ [Actuarial] Could not find DOM elements! Check your HTML IDs.");
    }
}

const getT = (key) => window.translations[localStorage.getItem('veritwin_lang') || 'en'][key] || key;

window.addEventListener('languageChanged', () => {
    if (riskChart) { riskChart.destroy(); riskChart = null; }
    if (ageChart) { ageChart.destroy(); ageChart = null; }
    if (genderChart) { genderChart.destroy(); genderChart = null; }
    if (vehicleChart) { vehicleChart.destroy(); vehicleChart = null; }
    if (behaviorChart) { behaviorChart.destroy(); behaviorChart = null; }
    if (vehicleAgeChart) { vehicleAgeChart.destroy(); vehicleAgeChart = null; }

    if (activeSubView === 'regional') {
        if (cachedSummaryData) renderRegionalCharts(cachedSummaryData);
    } else if (activeSubView === 'demographic') {
        if (cachedDemographicsData) renderDemographics(cachedDemographicsData);
    } else if (activeSubView === 'asset') {
        initPredictiveAsset();
    }
});

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
                    { label: getT('chart-reg-claims'), data: registered, backgroundColor: 'rgba(120, 120, 120, 0.6)' },
                    { label: getT('chart-proj-claims'), data: projected, backgroundColor: 'rgba(226, 185, 59, 0.9)' }
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
                // THE FIX: We removed the strict 'indexOf' array and now just count the items dynamically (i + 1)
                data: {
                    labels: Object.keys(d.age_groups).map((k, i) => getT('chart-age-' + (i + 1))),
                    datasets: [{ label: getT('chart-proj-claims'), data: Object.values(d.age_groups), backgroundColor: '#4CAF50' }]
                },
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
                data: { labels: Object.keys(d.genders).map(k => getT('chart-gender-' + k)), datasets: [{ data: Object.values(d.genders), backgroundColor: ['#2196F3', '#E91E63'], borderWidth: 0 }] },
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
                data: { labels: Object.keys(d.vehicle_types).map(k => getT('chart-veh-' + k)), datasets: [{ label: getT('chart-proj-claims-short'), data: Object.values(d.vehicle_types), backgroundColor: '#FF9800' }] },
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
                data: { labels: Object.keys(d.behaviors).map(k => getT('chart-beh-' + k)), datasets: [{ label: getT('chart-proj-claims-short'), data: Object.values(d.behaviors), backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'] }] },
                options: commonOptions
            });
        } else {
            behaviorChart.update('none');
        }

        if (!vehicleAgeChart) {
            console.log("🏗️ [Actuarial] Creating NEW vehicleAgeChart instance.");
            vehicleAgeChart = new Chart(document.getElementById('vehicleAgeChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.vehicle_ages).map(k => getT('chart-vehage-' + k)), datasets: [{ label: getT('chart-proj-claims-short'), data: Object.values(d.vehicle_ages), backgroundColor: '#9C27B0' }] },
                options: commonOptions
            });
        } else {
            vehicleAgeChart.update('none');
        }
        console.log("✅ [Actuarial] All demographics charts rendered/updated.");
    }, 50); // 50ms delay
}