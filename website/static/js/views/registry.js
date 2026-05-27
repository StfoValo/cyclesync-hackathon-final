/**
 * Vehicle Registry Module — Table, filters, pagination
 */
import { manufacturerBadge, powertrainIcon, iconBlackboxActive, iconBlackboxNone } from '/static/js/icons.js?v=18';

let currentPage = 1;
let currentSort = 'plate_number';
let currentOrder = 'asc';
let filterValues = {};

export async function initRegistry() {
    await loadFilterOptions();
    setupFilterListeners();
    setupPagination();
    setupSortHeaders();
    setupRegisterModal();
    loadRegistryTable();
}

async function loadFilterOptions() {
    try {
        const resp = await fetch('/api/db/vehicles/filters');
        filterValues = await resp.json();
        populateSelect('filter-manufacturer', filterValues.manufacturers);
        populateSelect('filter-powertrain', filterValues.powertrains);
        populateSelect('filter-region', filterValues.regions);
        populateSelect('filter-bodytype', filterValues.body_types);
    } catch (e) { console.error('Failed to load filters:', e); }
}

function populateSelect(id, options) {
    const sel = document.getElementById(id);
    if (!sel || !options) return;
    const first = sel.options[0].textContent;
    sel.innerHTML = `<option value="">${first}</option>` +
        options.map(o => `<option value="${o}">${o}</option>`).join('');
}

function getFilters() {
    const f = {};
    const q = document.getElementById('vehicle-search-input')?.value?.trim();
    if (q && q.length >= 2) f.q = q;
    const map = {manufacturer:'filter-manufacturer',powertrain:'filter-powertrain',region:'filter-region',
        body_type:'filter-bodytype',policy_status:'filter-policy',has_blackbox:'filter-blackbox'};
    for (const [k,id] of Object.entries(map)) {
        const v = document.getElementById(id)?.value;
        if (v) f[k] = v;
    }
    const model = document.getElementById('filter-model')?.value;
    if (model) f.model = model;
    return f;
}

export async function loadRegistryTable() {
    const tbody = document.getElementById('registry-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-slate-500">Loading...</td></tr>';

    const filters = getFilters();
    const params = new URLSearchParams({...filters, sort: currentSort, order: currentOrder, page: currentPage, per_page: 15});
    try {
        const resp = await fetch(`/api/db/vehicles?${params}`);
        const data = await resp.json();
        renderTable(data);
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-rose-400">Failed to load</td></tr>';
    }
}

function renderTable(data) {
    const tbody = document.getElementById('registry-table-body');
    if (!data.vehicles || data.vehicles.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-slate-500">No vehicles match filters</td></tr>';
        updatePagination(data);
        return;
    }
    tbody.innerHTML = data.vehicles.map(v => {
        const vsiColor = v.vsi_score >= 70 ? 'text-emerald-400' : v.vsi_score >= 40 ? 'text-amber-400' : 'text-rose-400';
        const polColor = v.policy_status === 'active'
            ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
            : 'bg-amber-500/20 text-amber-400 border-amber-500/30';
        const mfrBadge = manufacturerBadge(v.manufacturer, 'sm');
        const ptIcon   = powertrainIcon(v.powertrain, 'w-4 h-4');
        const bbIcon   = v.has_blackbox ? iconBlackboxActive() : iconBlackboxNone();
        return `<tr class="hover:bg-white/[0.03] cursor-pointer transition-colors registry-row" data-vin="${v.vin}">
            <td class="px-4 py-3"><span class="font-mono font-bold text-white text-xs bg-black/40 px-2 py-1 rounded border border-slate-700">${v.plate}</span></td>
            <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                    ${mfrBadge}
                    <div>
                        <div class="text-white font-medium text-sm">${v.model}</div>
                        <div class="text-xs text-slate-500">${v.manufacturer} · ${v.year || ''}</div>
                    </div>
                </div>
            </td>
            <td class="px-4 py-3 hidden md:table-cell text-slate-300 text-sm">${v.driver || '—'}</td>
            <td class="px-4 py-3 hidden lg:table-cell text-slate-400 text-sm">${v.region || '—'}</td>
            <td class="px-4 py-3"><span class="font-bold ${vsiColor}">${v.vsi_score ?? '—'}</span></td>
            <td class="px-4 py-3 hidden md:table-cell">${ptIcon}</td>
            <td class="px-4 py-3 hidden lg:table-cell"><span class="text-xs px-2 py-0.5 rounded-full border ${polColor} font-medium">${v.policy_status || '—'}</span></td>
            <td class="px-4 py-3 hidden lg:table-cell text-center">${bbIcon}</td>
            <td class="px-4 py-3 hidden xl:table-cell text-slate-400 text-sm">${v.odometer_km ? v.odometer_km.toLocaleString()+' km' : '—'}</td>
        </tr>`;
    }).join('');
    updatePagination(data);

    tbody.querySelectorAll('.registry-row').forEach(row => {
        row.addEventListener('click', () => {
            const vin = row.getAttribute('data-vin');
            window.dispatchEvent(new CustomEvent('open-passport', {detail: {vin}}));
        });
    });
}

function updatePagination(data) {
    document.getElementById('registry-count').textContent = `${data.total} vehicles`;
    document.getElementById('registry-page-info').textContent = `Page ${data.page} of ${data.pages}`;
    document.getElementById('btn-prev-page').disabled = data.page <= 1;
    document.getElementById('btn-next-page').disabled = data.page >= data.pages;
}

function setupPagination() {
    document.getElementById('btn-prev-page')?.addEventListener('click', () => { currentPage--; loadRegistryTable(); });
    document.getElementById('btn-next-page')?.addEventListener('click', () => { currentPage++; loadRegistryTable(); });
}

function setupSortHeaders() {
    document.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sort');
            if (currentSort === col) { currentOrder = currentOrder === 'asc' ? 'desc' : 'asc'; }
            else { currentSort = col; currentOrder = 'asc'; }
            currentPage = 1;
            loadRegistryTable();
        });
    });
}

function setupFilterListeners() {
    ['filter-manufacturer','filter-powertrain','filter-region','filter-bodytype','filter-policy','filter-blackbox'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', () => { currentPage = 1; loadRegistryTable(); });
    });
    document.getElementById('filter-manufacturer')?.addEventListener('change', async (e) => {
        const mfr = e.target.value;
        const modelSel = document.getElementById('filter-model');
        if (!mfr) { modelSel.innerHTML = '<option value="">All Models</option>'; modelSel.disabled = true; return; }
        try {
            const resp = await fetch(`/api/db/vehicles/models/${encodeURIComponent(mfr)}`);
            const data = await resp.json();
            modelSel.innerHTML = '<option value="">All Models</option>' + data.models.map(m => `<option value="${m}">${m}</option>`).join('');
            modelSel.disabled = false;
        } catch(e) { modelSel.disabled = true; }
    });
    document.getElementById('filter-model')?.addEventListener('change', () => { currentPage = 1; loadRegistryTable(); });
    document.getElementById('btn-clear-filters')?.addEventListener('click', () => {
        ['filter-manufacturer','filter-model','filter-powertrain','filter-region','filter-bodytype','filter-policy','filter-blackbox'].forEach(id => {
            const el = document.getElementById(id); if (el) el.value = '';
        });
        document.getElementById('filter-model').disabled = true;
        currentPage = 1; loadRegistryTable();
    });
}

function setupRegisterModal() {
    const modal = document.getElementById('register-modal');
    document.getElementById('btn-register-vehicle')?.addEventListener('click', () => modal?.classList.remove('hidden'));
    document.getElementById('btn-close-register')?.addEventListener('click', () => modal?.classList.add('hidden'));
    document.getElementById('btn-cancel-register')?.addEventListener('click', () => modal?.classList.add('hidden'));
    document.getElementById('register-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        const body = Object.fromEntries(fd.entries());
        try {
            await fetch('/api/db/vehicles', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
            modal.classList.add('hidden');
            e.target.reset();
            loadRegistryTable();
        } catch(err) { console.error('Registration failed:', err); }
    });
}


// Re-render the registry table when language toggles (some cells like
// powertrain label or policy status may be translatable).
window.addEventListener('languageChanged', () => {
    if (typeof loadVehicles === 'function') {
        try { loadVehicles(); } catch (_) { /* not initialized yet */ }
    }
});
