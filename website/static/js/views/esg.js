let tiresChart, brakesChart, batteriesChart;
let cachedEsgData = null;
let isInitialized = false;

export function initESG() {
    loadESGDashboard();
    if (!isInitialized) {
        setupReverseLogistics();
        isInitialized = true;
    }
}

const getT = (key) => window.translations[localStorage.getItem('veritwin_lang') || 'en'][key] || key;

window.addEventListener('languageChanged', () => {
    if (tiresChart) { tiresChart.destroy(); tiresChart = null; }
    if (brakesChart) { brakesChart.destroy(); brakesChart = null; }
    if (batteriesChart) { batteriesChart.destroy(); batteriesChart = null; }
    if (cachedEsgData) renderESG(cachedEsgData);
});

function setupReverseLogistics() {
    const btn = document.getElementById('btn-generate-manifest');
    const terminal = document.getElementById('logistics-terminal');
    const regionSelect = document.getElementById('logistics-region');

    if (!btn || !terminal || !regionSelect) return;

    btn.addEventListener('click', () => {
        const region = regionSelect.value;

        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = getT('term-run') + '...';

        terminal.innerHTML = '';

        // Sleek UI Status Indicators instead of CLI text
        const spinnerSVG = `<svg class="w-4 h-4 text-brand-500 animate-spin inline-block mr-2" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
        const checkSVG = `<svg class="w-4 h-4 text-emerald-400 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`;

        setTimeout(() => { terminal.innerHTML += `<div id="step1" class="text-slate-300 mb-2">${spinnerSVG} Ingesting OEM Blueprints...</div>`; }, 0);
        setTimeout(() => {
            document.getElementById('step1').innerHTML = `${checkSVG} OEM Blueprints Ingested.`;
            terminal.innerHTML += `<div id="step2" class="text-slate-300 mb-2">${spinnerSVG} Analyzing VSI degradation profiles...</div>`;
        }, 600);
        setTimeout(() => {
            document.getElementById('step2').innerHTML = `${checkSVG} Degradation Profiles Analyzed.`;
            terminal.innerHTML += `<div id="step3" class="text-slate-300 mb-4">${spinnerSVG} Cross-referencing local recycling network...</div>`;
        }, 1200);

        setTimeout(async () => {
            try {
                // THE FIX: Grab the language and attach it to the API URL
                const currentLang = localStorage.getItem('veritwin_lang') || 'en';
                const response = await fetch(`/api/ai/circular-logistics/${encodeURIComponent(region)}?lang=${currentLang}`);
                if (!response.ok) throw new Error("HTTP error " + response.status);

                // Setup the Stream Reader
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let fullText = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    // Decode the chunk
                    const chunk = decoder.decode(value);
                    fullText += chunk;

                    // Let marked.js perfectly parse the markdown into HTML!
                    terminal.innerHTML = marked.parse(fullText); // Replace 'terminal' with whatever variable holds your UI bubble

                    // Add the prose-ai class to ensure our table CSS applies
                    terminal.classList.add('prose-ai');
                    terminal.scrollTop = terminal.scrollHeight;
                }
            } catch (error) {
                console.error("Logistics API Error:", error);
                terminal.innerHTML = `<div class="text-red-400 p-4 bg-red-400/10 rounded-lg border border-red-400/20">⚠️ System Timeout: Unable to generate manifest.</div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
        }, 1800);
    });
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
        data: { labels: Object.keys(tiresData).map(k => getT('chart-' + k.split('_')[0])), datasets: [{ data: Object.values(tiresData), backgroundColor: ecoColors1, borderWidth: 0 }] },
        options: chartOptions
    });

    // Brakes
    const brakesData = circular.recovered_brakes.destinations;
    if (brakesChart) brakesChart.destroy();
    brakesChart = new window.Chart(document.getElementById('esgBrakesChart'), {
        type: 'doughnut',
        data: { labels: Object.keys(brakesData).map(k => getT('chart-' + k.split('_')[0])), datasets: [{ data: Object.values(brakesData), backgroundColor: ecoColors2, borderWidth: 0 }] },
        options: chartOptions
    });

    // Batteries
    const batteriesData = circular.recovered_ev_batteries.destinations;
    if (batteriesChart) batteriesChart.destroy();
    batteriesChart = new window.Chart(document.getElementById('esgBatteriesChart'), {
        type: 'doughnut',
        data: { labels: Object.keys(batteriesData).map(k => getT('chart-' + k.split('_')[0])), datasets: [{ data: Object.values(batteriesData), backgroundColor: ecoColors3, borderWidth: 0 }] },
        options: chartOptions
    });
}