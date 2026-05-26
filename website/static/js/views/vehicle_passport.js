/**
 * Vehicle Digital Passport — works with new DB-backed API
 */
import { manufacturerBadge, powertrainIcon, componentIcon, iconBlackboxActive } from '/static/js/icons.js?v=18';
import { renderCategorizedTelemetry } from './telemetry_panel.js?v=4';

let currentPassportData = null;

export function initVehiclePassport() {
    const searchInput = document.getElementById('vehicle-search-input');
    const searchDropdown = document.getElementById('vehicle-search-dropdown');
    const closeBtn = document.getElementById('btn-close-passport');
    if (!searchInput) return;

    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const q = e.target.value.trim();
            if (q.length >= 2) fetchSearchResults(q);
            else searchDropdown.classList.add('hidden');
        }, 250);
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) searchDropdown.classList.add('hidden');
    });

    searchInput.addEventListener('focus', () => { if (searchInput.value.trim().length >= 2) fetchSearchResults(searchInput.value.trim()); });
    searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter' && searchInput.value.trim().length >= 2) fetchSearchResults(searchInput.value.trim()); });

    document.getElementById('btn-search-vehicle')?.addEventListener('click', () => {
        if (searchInput.value.trim().length >= 2) fetchSearchResults(searchInput.value.trim());
    });

    if (closeBtn) closeBtn.addEventListener('click', closePassport);

    // Listen for row clicks from registry
    window.addEventListener('open-passport', (e) => { if (e.detail?.vin) loadPassportByVin(e.detail.vin); });

    // Accordion toggles
    document.querySelectorAll('.accordion-trigger').forEach(btn => {
        btn.addEventListener('click', () => {
            const content = document.getElementById(btn.getAttribute('data-target'));
            const chevron = btn.querySelector('.accordion-chevron');
            if (content) {
                content.classList.toggle('hidden');
                if (chevron) chevron.style.transform = content.classList.contains('hidden') ? '' : 'rotate(180deg)';
            }
        });
    });
}

function closePassport() {
    document.getElementById('vehicle-passport-panel')?.classList.add('hidden');
    document.getElementById('map-view-panel')?.classList.remove('hidden');
    document.getElementById('registry-view-panel')?.classList.remove('hidden');
    currentPassportData = null;
}

async function fetchSearchResults(query) {
    const dropdown = document.getElementById('vehicle-search-dropdown');
    try {
        const resp = await fetch(`/api/vehicles/search?q=${encodeURIComponent(query)}`);
        const results = await resp.json();
        renderDropdown(results);
    } catch (err) { dropdown.classList.add('hidden'); }
}

function renderDropdown(results) {
    const dropdown = document.getElementById('vehicle-search-dropdown');
    if (!results?.length) {
        dropdown.innerHTML = '<div class="px-4 py-3 text-slate-500 text-sm">No vehicles found</div>';
        dropdown.classList.remove('hidden'); return;
    }
    dropdown.innerHTML = results.map(v => {
        const vsiColor = v.vsi >= 70 ? 'text-emerald-400' : v.vsi >= 40 ? 'text-amber-400' : 'text-rose-400';
        return `<button class="vehicle-search-result w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors text-left border-b border-white/5 last:border-0" data-plate="${v.plate}">
            <div class="flex items-center gap-3">
                <span class="font-mono font-bold text-white text-sm bg-black/40 px-2 py-1 rounded border border-slate-700">${v.plate}</span>
                ${manufacturerBadge(v.manufacturer, 'sm')}
                <div><div class="text-sm font-medium text-white">${v.model}</div><div class="text-xs text-slate-400">${v.driver}</div></div>
            </div>
            <span class="font-bold text-sm ${vsiColor}">${v.vsi}/100</span>
        </button>`;
    }).join('');
    dropdown.classList.remove('hidden');
    dropdown.querySelectorAll('.vehicle-search-result').forEach(btn => {
        btn.addEventListener('click', () => {
            const plate = btn.getAttribute('data-plate');
            loadPassportByPlate(plate);
            dropdown.classList.add('hidden');
            document.getElementById('vehicle-search-input').value = plate;
        });
    });
}

async function loadPassportByPlate(plate) {
    try {
        const resp = await fetch(`/api/vehicles/${encodeURIComponent(plate)}/passport`);
        const data = await resp.json();
        if (data.error) return;
        showPassport(data);
    } catch (err) { console.error('Passport load failed:', err); }
}

async function loadPassportByVin(vin) {
    try {
        const resp = await fetch(`/api/db/vehicles/${encodeURIComponent(vin)}`);
        const data = await resp.json();
        if (data.error) return;
        showPassport(data);
    } catch (err) { console.error('Passport load failed:', err); }
}

function showPassport(data) {
    currentPassportData = data;
    renderPassport(data);
    const panel = document.getElementById('vehicle-passport-panel');
    panel.classList.remove('hidden');
    document.getElementById('map-view-panel')?.classList.add('hidden');
    document.getElementById('registry-view-panel')?.classList.add('hidden');
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderPassport(data) {
    const id = data.identity || {};
    const ins = data.insurance || {};
    const tel = data.telemetry || {};

    // Header
    document.getElementById('passport-model').textContent = `${id.manufacturer || ''} ${id.model || ''}`.trim() || '—';
    document.getElementById('passport-plate').textContent = data.plate || '—';
    document.getElementById('passport-driver').textContent = `${id.driver || '—'}`;

    const ptEl = document.getElementById('passport-powertrain');
    if (ptEl) ptEl.innerHTML = `<span class="inline-flex items-center gap-1.5">${powertrainIcon(id.powertrain, 'w-3.5 h-3.5')}<span class="text-xs">${({electric:'Electric',diesel:'Diesel',petrol:'Petrol',hybrid:'Hybrid',plug_in_hybrid:'PHEV',gpl:'GPL'})[id.powertrain] || id.powertrain || '—'}</span></span>`;

    const bbBadge = document.getElementById('passport-blackbox');
    if (tel.has_blackbox) {
        bbBadge.classList.remove('hidden');
        bbBadge.className = 'inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-400 border border-brand-500/30 font-medium';
        bbBadge.innerHTML = `<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Blackbox Active`;
    } else { bbBadge.classList.add('hidden'); }

    // Manufacturer badge in the icon slot
    const iconEl = document.getElementById('passport-icon');
    if (iconEl) iconEl.innerHTML = manufacturerBadge(id.manufacturer, 'lg');

    // VSI
    const vsiEl = document.getElementById('passport-vsi');
    const vsi = tel.driving_score ?? data.vsi_score ?? '—';
    vsiEl.textContent = `${vsi}/100`;
    vsiEl.className = 'text-3xl font-black ' + (vsi >= 70 ? 'text-emerald-400' : vsi >= 40 ? 'text-amber-400' : 'text-rose-400 animate-pulse');

    // Components — now an array from DB
    renderComponents(data.components || []);

    // Insurance
    const insBadge = document.getElementById('passport-insurance-badge');
    insBadge.textContent = ins.policy_status || '—';
    insBadge.className = 'text-xs px-2 py-0.5 rounded-full font-medium ' +
        (ins.policy_status === 'active' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30');

    const insGrid = document.getElementById('passport-insurance-grid');
    insGrid.innerHTML = _cell('Policy Type', ins.policy_type) + _cell('Insurer', ins.insurer) +
        _cell('Premium', ins.premium_eur ? `€${ins.premium_eur.toLocaleString()}` : '—') +
        _cell('Telematics Discount', ins.telematics_discount ? `${ins.telematics_discount}%` : '—') +
        _cell('Expiry', ins.policy_expiry) + _cell('Claims', `${ins.claims_count ?? 0}`) +
        _cell('VIN', `<span class="font-mono text-xs">${data.vin || '—'}</span>`) +
        _cell('Policy #', `<span class="font-mono text-xs">${ins.policy_number || '—'}</span>`);

    // Telemetry
    renderTelemetry(tel);

    // Maintenance
    renderMaintenance(data.maintenance || []);
}

function renderComponents(components) {
    const container = document.getElementById('passport-components');
    if (!components.length) { container.innerHTML = '<div class="text-slate-500 text-sm col-span-4">No components data</div>'; return; }

    // Group by category
    const groups = {};
    components.forEach(c => {
        const cat = c.category || 'unknown';
        if (!groups[cat]) groups[cat] = [];
        groups[cat].push(c);
    });

    const catLabels = { tire:'Tires', brake_pad:'Brakes', ev_battery:'Battery', brake_disc:'Discs' };

    container.innerHTML = Object.entries(groups).map(([cat, items]) => {
        const icon = componentIcon(cat, 'w-5 h-5');
        const label = catLabels[cat] || cat;
        const avgWear = Math.round(items.reduce((s,c) => s + (c.wear_percent||0), 0) / items.length);
        const healthPct = 100 - avgWear;
        const worst = items.reduce((w,c) => (c.wear_percent||0) > (w.wear_percent||0) ? c : w, items[0]);
        const status = worst.health_status || (avgWear > 80 ? 'critical' : avgWear > 60 ? 'warning' : 'healthy');
        const color = status === 'critical' ? 'text-rose-400' : status === 'warning' ? 'text-amber-400' : 'text-emerald-400';
        const barColor = status === 'critical' ? 'bg-rose-500' : status === 'warning' ? 'bg-amber-500' : 'bg-emerald-500';
        const borderColor = status === 'critical' ? 'border-rose-500/30' : status === 'warning' ? 'border-amber-500/30' : 'border-emerald-500/30';
        const detail = items.map(c => `${c.position||''}: ${c.wear_percent||0}%`).join(', ');

        return `<div class="bg-slate-800/50 rounded-lg p-4 border ${borderColor}" title="${detail}">
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2 ${color}">${icon}<span class="font-semibold text-white text-sm">${label}</span></div>
                <span class="text-xs font-bold ${color} uppercase">${status}</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-2 mb-2"><div class="${barColor} rounded-full h-2 transition-all duration-1000" style="width:${healthPct}%"></div></div>
            <div class="flex justify-between text-xs"><span class="${color} font-bold">${healthPct}%</span><span class="text-slate-500 truncate ml-2">${items.length} components</span></div>
        </div>`;
    }).join('');
}

function renderTelemetry(tel) {
    const grid = document.getElementById('passport-telemetry-grid');
    if (!grid) return;

    // Compact "overview" row reusing the legacy live fields (rendered with their
    // existing colour-coding so the dashboard look stays the same).
    const overviewHtml = (tel && tel.vin) ? `
        <div class="col-span-2 sm:col-span-4 grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2">
            ${_cell('Odometer', tel.current_odometer_km ? `${tel.current_odometer_km.toLocaleString()} km` : '—')}
            ${_cell('Driving Score', tel.driving_score != null ? `<span class="${tel.driving_score >= 70 ? 'text-emerald-400' : tel.driving_score >= 40 ? 'text-amber-400' : 'text-rose-400'} font-bold">${tel.driving_score}/100</span>` : '—')}
            ${_cell('Last Sync', tel.last_sync_timestamp ? `<span class="font-mono text-xs">${new Date(tel.last_sync_timestamp).toLocaleString()}</span>` : '—')}
            ${_cell('Avg Speed', tel.avg_speed_kmh ? `${tel.avg_speed_kmh} km/h` : '—')}
        </div>` : '';

    // Full categorised raw-signal panel below (all 126 columns × 18 sections).
    renderCategorizedTelemetry(grid, tel, { overviewHtml });
}

function renderMaintenance(events) {
    const container = document.getElementById('passport-history-timeline');
    if (!events?.length) { container.innerHTML = '<div class="text-slate-500 text-sm pl-6">No maintenance records</div>'; return; }
    container.innerHTML = events.map(h => {
        const colors = {critical:'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)] animate-pulse',alert:'bg-rose-500',warning:'bg-amber-500',notification:'bg-brand-500',info:'bg-slate-400',scheduled:'bg-slate-400'};
        const dotColor = colors[h.severity || h.event_type] || 'bg-slate-400';
        const textColor = (h.severity === 'critical' || h.event_type === 'critical') ? 'text-rose-400 font-bold' : 'text-white';
        return `<div class="relative pl-6">
            <div class="absolute w-3 h-3 ${dotColor} rounded-full -left-[7px] top-1.5 border-2 border-[#0f172a]"></div>
            <p class="text-xs text-slate-500 mb-0.5">${h.event_date || '—'}</p>
            <p class="text-sm font-medium ${textColor}">${h.description || h.event || '—'}</p>
        </div>`;
    }).join('');
}

function _cell(label, value) {
    return `<div class="bg-slate-800/50 rounded p-3 border border-white/5"><p class="text-xs text-slate-400 mb-1">${label}</p><p class="text-white font-medium">${value || '—'}</p></div>`;
}
