document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const viewSections = document.querySelectorAll('.view-section');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            // Remove active class from all nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked nav item
            const currentItem = e.currentTarget;
            currentItem.classList.add('active');

            // Hide all view sections
            viewSections.forEach(section => {
                section.classList.remove('active');
            });

            // Show targeted view section
            const targetId = currentItem.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                if (targetId === 'telemetry-view') {
                    const mapFrame = document.getElementById('map-frame');
                    if (mapFrame && !mapFrame.src.includes('/api/fleet/map')) {
                        mapFrame.src = '/api/fleet/map';
                    }
                }
            }
        });
    });

    // Initialize map on load
    const mapFrame = document.getElementById('map-frame');
    if (mapFrame) {
        mapFrame.src = '/api/fleet/map?view=fleet';
    }

    // Map View Toggle Logic
    const btnViewFleet = document.getElementById('btn-view-fleet');
    const btnViewSuppliers = document.getElementById('btn-view-suppliers');

    if (btnViewFleet && btnViewSuppliers && mapFrame) {
        btnViewFleet.addEventListener('click', () => {
            btnViewFleet.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewFleet.classList.remove('text-slate-400', 'hover:text-white');
            
            btnViewSuppliers.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewSuppliers.classList.add('text-slate-400', 'hover:text-white');
            
            mapFrame.src = '/api/fleet/map?view=fleet';
        });

        btnViewSuppliers.addEventListener('click', () => {
            btnViewSuppliers.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewSuppliers.classList.remove('text-slate-400', 'hover:text-white');
            
            btnViewFleet.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewFleet.classList.add('text-slate-400', 'hover:text-white');
            
            mapFrame.src = '/api/fleet/map?view=suppliers';
        });
    }

    // Executive View Toggle Logic
    const btnViewRegional = document.getElementById('btn-view-regional');
    const btnViewDemographic = document.getElementById('btn-view-demographic');
    const regionalCharts = document.getElementById('regional-charts');
    const demographicCharts = document.getElementById('demographic-charts');

    if (btnViewRegional && btnViewDemographic && regionalCharts && demographicCharts) {
        btnViewRegional.addEventListener('click', () => {
            btnViewRegional.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.remove('text-slate-400', 'hover:text-white');
            
            btnViewDemographic.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.add('text-slate-400', 'hover:text-white');
            
            regionalCharts.classList.remove('hidden');
            demographicCharts.classList.add('hidden');
        });

        btnViewDemographic.addEventListener('click', () => {
            btnViewDemographic.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewDemographic.classList.remove('text-slate-400', 'hover:text-white');
            
            btnViewRegional.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewRegional.classList.add('text-slate-400', 'hover:text-white');
            
            demographicCharts.classList.remove('hidden');
            regionalCharts.classList.add('hidden');
        });
    }

    async function loadExecutiveSummary() {
        try {
            const res = await fetch('/api/actuarial/summary');
            if (!res.ok) throw new Error("HTTP error " + res.status);
            const data = await res.json();
            const kpis = data.kpis;
            const regional = data.regional_breakdown;

            document.getElementById('kpi-total-fleet').innerText = kpis.total_monitored_fleet.toLocaleString();
            document.getElementById('kpi-avg-premium').innerText = '€' + kpis.average_premium_eur.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
            
            const discountElem = document.getElementById('kpi-discount');
            discountElem.innerText = kpis.average_discount_pct.toFixed(1) + '%';
            if (kpis.average_discount_pct < 0) {
                discountElem.classList.replace('text-emerald-400', 'text-emerald-500'); 
            } else {
                discountElem.classList.replace('text-emerald-400', 'text-red-500'); 
            }
            
            document.getElementById('kpi-claims-reduction').innerText = kpis.claims_reduction_pct.toFixed(1) + '%'; 

            // Render Regional Chart
            const regions = regional.map(r => r.region);
            const projected = regional.map(r => r.projected_accidents);
            const registered = regional.map(r => r.registered_claims);

            Chart.defaults.color = '#aaa';
            Chart.defaults.borderColor = '#333'; 

            new Chart(document.getElementById('riskChart'), {
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
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: { 
                        y: { grid: { color: '#333' }, ticks: { color: '#aaa' } }, 
                        x: { grid: { display: false }, ticks: { color: '#aaa' } } 
                    } 
                }
            });

        } catch (error) {
            console.error("Failed to load executive summary:", error);
        }
    }

    async function loadDemographics() {
        try {
            const res = await fetch('/api/actuarial/deep-dive');
            const d = await res.json();

            Chart.defaults.color = '#aaa';
            Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

            new Chart(document.getElementById('ageChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.age_groups), datasets: [{ label: 'Projected Claims', data: Object.values(d.age_groups), backgroundColor: '#4CAF50' }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            new Chart(document.getElementById('genderChart'), {
                type: 'doughnut',
                data: { labels: Object.keys(d.genders), datasets: [{ data: Object.values(d.genders), backgroundColor: ['#2196F3', '#E91E63'], borderWidth: 0 }] },
                options: { responsive: true, maintainAspectRatio: false, cutout: '70%' }
            });

            new Chart(document.getElementById('vehicleChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.vehicle_types), datasets: [{ label: 'Projected Claims', data: Object.values(d.vehicle_types), backgroundColor: '#FF9800' }] },
                options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

            new Chart(document.getElementById('behaviorChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.behaviors), datasets: [{ label: 'Projected Claims', data: Object.values(d.behaviors), backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'] }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
            
            new Chart(document.getElementById('vehicleAgeChart'), {
                type: 'bar',
                data: { labels: Object.keys(d.vehicle_ages), datasets: [{ label: 'Projected Claims', data: Object.values(d.vehicle_ages), backgroundColor: '#9C27B0' }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });

        } catch (error) {
            console.error("Failed to load demographics:", error);
        }
    }

    async function loadVSIDashboard() {
        try {
            const res = await fetch('/api/actuarial/vsi');
            if (!res.ok) throw new Error("HTTP error " + res.status);
            const p = await res.json();
            
            const metrics = p.metrics;
            const vsiVal = metrics.avg_vsi_score;
            const kpiVsi = document.getElementById('kpi-vsi');
            if (kpiVsi) {
                kpiVsi.innerText = `${vsiVal.toFixed(1)}/100`;
                kpiVsi.className = `text-3xl font-bold ${vsiVal > 75 ? 'text-emerald-400' : vsiVal > 60 ? 'text-amber-400' : 'text-red-500'}`;
            }
            
            const kpiCritical = document.getElementById('kpi-critical');
            if (kpiCritical) kpiCritical.innerText = parseInt(metrics.total_critical_assets).toLocaleString();
            
            const kpiHardware = document.getElementById('kpi-hardware-cost');
            if (kpiHardware) kpiHardware.innerText = '€' + metrics.projected_hardware_claims_eur.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

            const cleanRegional = p.regional.filter(r => !r.region.includes("Unipol") && r.region.trim() !== "");
            const regions = cleanRegional.map(r => r.region);
            
            const vsiS = cleanRegional.map(r => r.vsi[0]);
            const vsiW = cleanRegional.map(r => r.vsi[1]);
            const vsiC = cleanRegional.map(r => r.vsi[2]);
            
            const brkS = cleanRegional.map(r => r.brakes[0]);
            const brkW = cleanRegional.map(r => r.brakes[1]);
            const brkC = cleanRegional.map(r => r.brakes[2]);
            
            const tirS = cleanRegional.map(r => r.tires[0]);
            const tirW = cleanRegional.map(r => r.tires[1]);
            const tirC = cleanRegional.map(r => r.tires[2]);

            const gVsi = Object.values(p.global.overall_vsi);
            const gBrk = Object.values(p.global.brakes);
            const gTir = Object.values(p.global.tires);

            Chart.register(ChartDataLabels);
            Chart.defaults.color = '#aaa';
            Chart.defaults.borderColor = '#333'; 

            const commonStackOptions = {
                responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: { 
                    legend: { position: 'bottom', labels: { color: '#fff' } },
                    datalabels: { display: false } 
                },
                scales: { x: { stacked: true, grid: { color: '#333' } }, y: { stacked: true, grid: { display: false } } }
            };

            new Chart(document.getElementById('vsiRegionChart'), { type: 'bar', data: { labels: regions, datasets: [
                { label: 'Safe', data: vsiS, backgroundColor: '#00A67E' },
                { label: 'Warning', data: vsiW, backgroundColor: '#E2B93B' },
                { label: 'Critical', data: vsiC, backgroundColor: '#FF5A5A' } ]}, options: commonStackOptions });

            new Chart(document.getElementById('brakeRegionChart'), { type: 'bar', data: { labels: regions, datasets: [
                { label: 'Safe (>6mm)', data: brkS, backgroundColor: '#00A67E' },
                { label: 'Warning (3-6mm)', data: brkW, backgroundColor: '#E2B93B' },
                { label: 'Critical (<3mm)', data: brkC, backgroundColor: '#FF5A5A' } ]}, options: commonStackOptions });

            new Chart(document.getElementById('tireRegionChart'), { type: 'bar', data: { labels: regions, datasets: [
                { label: 'Safe (>4mm)', data: tirS, backgroundColor: '#00A67E' },
                { label: 'Warning (2-4mm)', data: tirW, backgroundColor: '#E2B93B' },
                { label: 'Critical (<2mm)', data: tirC, backgroundColor: '#FF5A5A' } ]}, options: commonStackOptions });

            const dOptions = { 
                responsive: true, 
                maintainAspectRatio: false, 
                cutout: '65%', 
                plugins: { 
                    legend: { position: 'bottom' },
                    datalabels: {
                        color: '#fff',
                        font: { weight: 'bold', size: 12 },
                        formatter: (value, ctx) => {
                            let sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            if (sum === 0) return '';
                            let pct = (value * 100 / sum).toFixed(1) + '%';
                            return (value * 100 / sum) > 5 ? pct : '';
                        }
                    }
                } 
            };

            new Chart(document.getElementById('vsiGlobalChart'), { type: 'doughnut', data: { labels: ['Safe', 'Warning', 'Critical'], datasets: [{ data: gVsi, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }]}, options: dOptions });
            new Chart(document.getElementById('brakeGlobalChart'), { type: 'doughnut', data: { labels: ['Safe', 'Warning', 'Critical'], datasets: [{ data: gBrk, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }]}, options: dOptions });
            new Chart(document.getElementById('tireGlobalChart'), { type: 'doughnut', data: { labels: ['Safe', 'Warning', 'Critical'], datasets: [{ data: gTir, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }]}, options: dOptions });
            
        } catch (error) {
            console.error("Failed to load VSI dashboard:", error);
        }
    }

    loadDemographics();
    loadExecutiveSummary();
    loadVSIDashboard();
    
    // AI Terminal Streaming Logic
    const btnAnalyze = document.getElementById('btn-analyze');
    const regionSelector = document.getElementById('region-selector');
    const aiTerminal = document.getElementById('ai-terminal');

    if (btnAnalyze && regionSelector && aiTerminal) {
        btnAnalyze.addEventListener('click', async () => {
            const region = regionSelector.value;
            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = "Orchestrating Network...";
            
            aiTerminal.innerHTML = `<b style='color: #00A67E;'>[INIT]</b> Ingesting VSI Telemetry and Local Supply Chain for <b>${region}</b>...\n\n`;

            try {
                const response = await fetch(`/api/ai/orchestrate/${region}`);
                const reader = response.body.getReader();
                const decoder = new TextDecoder("utf-8");

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    const cleanChunk = chunk.replace(/###/g, '\n\n>>').replace(/\*\*/g, '');
                    aiTerminal.innerHTML += cleanChunk;
                    aiTerminal.scrollTop = aiTerminal.scrollHeight;
                }
                
                aiTerminal.innerHTML += "\n\n<b style='color: #00A67E;'>[PROCESS COMPLETE]</b> Directives ready for dispatch.";
            } catch (error) {
                aiTerminal.innerHTML += `\n\n<b style='color: #FF5A5A;'>[ERROR]</b> ${error.message}`;
            } finally {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = `<svg class="w-5 h-5 inline-block mr-2 -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>Generate Intervention Strategy`;
            }
        });
    }

    console.log("CycleSync Frontend Shell Initialized.");
});
