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

function setupReverseLogistics() {
    const btn = document.getElementById('btn-generate-manifest');
    const terminal = document.getElementById('logistics-terminal');
    const regionSelect = document.getElementById('logistics-region');

    if (!btn || !terminal || !regionSelect) return;

    btn.addEventListener('click', () => {
        const region = regionSelect.value;

        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = 'Scanning Fleet Telemetry...';

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
                const response = await fetch(`/api/ai/circular-logistics/${encodeURIComponent(region)}`);
                if (!response.ok) throw new Error("HTTP error " + response.status);

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                // Clear the loading steps and create a container for the parsed text
                terminal.innerHTML = '<div id="manifest-content"></div>';
                const contentDiv = document.getElementById('manifest-content');
                let fullText = ""; // The Accumulator

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    fullText += chunk; // Add to accumulator

                    // Safely format the ENTIRE accumulated text
                    let formattedText = fullText;

                    // --- NEW: Auto-Branding Filter ---
                    // Globally, case-insensitively replace "UNIPOL" with "CycleSync"
                    formattedText = formattedText.replace(/UNIPOL/gi, 'CycleSync');

                    // 1. Headers (### Heading)
                    formattedText = formattedText.replace(/### (.*?)(?:\n|$)/g, '<h4 class="text-white font-bold text-lg border-b border-white/10 pb-2 mt-6 mb-3 flex items-center gap-2"><svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>$1</h4>');

                    // 2. Bold Text (**text**)
                    formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-400 font-semibold">$1</strong>');

                    // 3. Bullet Points (* text)
                    formattedText = formattedText.replace(/^\* (.*?)(?:\n|$)/gm, '<div class="flex items-start gap-3 mb-2 mt-2"><span class="text-emerald-500 mt-1 text-lg leading-none">•</span><span class="text-slate-300">$1</span></div>');

                    // 4. Standard Line Breaks
                    formattedText = formattedText.replace(/\n/g, '<br>');

                    // Replace the inner HTML with the perfectly formatted string
                    contentDiv.innerHTML = formattedText;
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