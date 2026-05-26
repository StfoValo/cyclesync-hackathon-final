// static/js/driver/profile_view.js
//
// Renders the "Gestione" tab. Combines the partner's vehicle-identity / policy
// / next-service blocks with the baseline's driver-info card, full garage
// list (pin / unlink), add-vehicle form, and maintenance-log form.

const DRIVER_ID = 1;


function getDriverInitials(name) {
    if (!name) return 'AM';
    return name.split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase();
}


export function renderProfileView(vehicle) {
    const container = document.getElementById('profile-content-container');
    if (!container) return;

    const lang = localStorage.getItem('veritwin_lang') || 'it';
    const t = (window.translations && window.translations[lang]) || window.translations?.['it'] || {};

    const driver = window._driverProfile || {};
    const allVehicles = window._driverVehicles || [];

    const v = vehicle || allVehicles[0] || {};
    const serviceInterval = 20000;
    const currentOdo = v.odometer_km || 0;
    const kmSinceLastService = currentOdo % serviceInterval;
    const kmToNextService = serviceInterval - kmSinceLastService;
    const servicePct = (kmSinceLastService / serviceInterval) * 100;

    container.innerHTML = `
        ${renderDriverInfo(driver, lang, t)}
        ${renderVehicleIdentity(v, lang, t)}
        ${renderPolicyBlock(lang, t)}
        ${renderConnectedServices(lang, t)}
        ${renderNextService(kmToNextService, servicePct, lang, t)}
        ${renderGarageList(allVehicles, lang, t)}
        ${renderAddVehicleForm(lang, t)}
        ${renderMaintenanceForm(v, lang, t)}
    `;
    wireProfileHandlers();
}


function renderDriverInfo(driver, lang, t) {
    const name = driver.display_name || '—';
    const email = driver.email || '—';
    const phone = driver.phone || '—';
    return `
        <div class="glass-card p-4 mb-4 border border-white/5">
            <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-full bg-brand-600 flex items-center justify-center text-lg font-bold text-black shrink-0">
                    ${getDriverInitials(name)}
                </div>
                <div class="min-w-0 flex-1">
                    <p class="font-bold text-white text-base truncate">${name}</p>
                    <p class="text-xs text-slate-400 truncate">${email}</p>
                    <p class="text-[10px] text-slate-500">${phone}</p>
                </div>
            </div>
        </div>`;
}


function renderVehicleIdentity(v, lang, t) {
    return `
        <div class="glass-card p-4 mb-4 border border-white/5">
            <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">${t['driver-id-veicolo'] || (lang === 'en' ? 'Vehicle Identity' : 'Identità Veicolo')}</h3>
            <div class="grid grid-cols-2 gap-y-4 gap-x-2">
                <div>
                    <p class="text-[10px] text-slate-500 mb-0.5">${t['driver-plate'] || (lang === 'en' ? 'Plate' : 'Targa')}</p>
                    <p class="text-sm font-bold text-white uppercase">${v.plate || '--'}</p>
                </div>
                <div>
                    <p class="text-[10px] text-slate-500 mb-0.5">${t['driver-year'] || (lang === 'en' ? 'Year' : 'Anno')}</p>
                    <p class="text-sm font-bold text-white">${v.year || '--'}</p>
                </div>
                <div class="col-span-2">
                    <p class="text-[10px] text-slate-500 mb-0.5">${t['driver-vin'] || (lang === 'en' ? 'VIN' : 'VIN (Telaio)')}</p>
                    <p class="text-xs font-mono font-bold text-slate-300 tracking-wider bg-slate-800/50 p-2 rounded-lg border border-white/5 inline-block">${v.vin || '--'}</p>
                </div>
            </div>
        </div>`;
}


function renderPolicyBlock(lang, t) {
    return `
        <div class="glass-card p-4 mb-4 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.05)] relative overflow-hidden group">
            <div class="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none"></div>
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-[11px] font-bold text-emerald-400 uppercase tracking-widest">${t['driver-polizza'] || (lang === 'en' ? 'CycleSync Policy' : 'Polizza VeriTwin')}</h3>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">${t['driver-active'] || (lang === 'en' ? 'Active' : 'Attiva')}</span>
            </div>
            <div class="flex items-end justify-between mb-2">
                <div>
                    <p class="text-[10px] text-slate-400 mb-0.5">${t['driver-expiry'] || (lang === 'en' ? 'Expiry' : 'Scadenza Copertura')}</p>
                    <p class="text-base font-bold text-white">${t['driver-expiry-date'] || '12 Maggio 2027'}</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] text-brand-400 mb-0.5">${t['driver-discount'] || (lang === 'en' ? 'Discount applied' : 'Sconto applicato')}</p>
                    <p class="text-xl font-black text-brand-400">-14%</p>
                </div>
            </div>
        </div>`;
}


function renderConnectedServices(lang, t) {
    return `
        <div class="glass-card p-4 mb-4 border border-white/5">
            <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">${t['driver-servizi'] || (lang === 'en' ? 'Connected Services' : 'Servizi Connessi')}</h3>
            <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl mb-2 border border-white/5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-base">⚡</div>
                    <div>
                        <p class="text-sm font-bold text-white">${t['driver-telepass'] || (lang === 'en' ? 'European Telepass' : 'Telepass Europeo')}</p>
                        <p class="text-[10px] text-slate-400">${t['driver-telepass-desc'] || (lang === 'en' ? 'Device linked to plate' : 'Dispositivo associato alla targa')}</p>
                    </div>
                </div>
                <div class="w-8 h-4 bg-blue-500 rounded-full relative cursor-pointer shadow-[0_0_10px_rgba(59,130,246,0.3)]">
                    <div class="absolute right-0.5 top-0.5 w-3 h-3 bg-white rounded-full"></div>
                </div>
            </div>
            <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl border border-white/5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center text-rose-400 text-base">🛟</div>
                    <div>
                        <p class="text-sm font-bold text-white">${t['driver-roadside'] || (lang === 'en' ? 'Roadside Assistance' : 'Soccorso Stradale')}</p>
                        <p class="text-[10px] text-slate-400">${t['driver-roadside-desc'] || (lang === 'en' ? 'Included with policy' : 'Incluso nella polizza')}</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-emerald-400">${t['driver-active-masc'] || (lang === 'en' ? 'Active' : 'Attivo')}</span>
            </div>
        </div>`;
}


function renderNextService(kmToNextService, servicePct, lang, t) {
    return `
        <div class="glass-card p-4 mb-4 border border-white/5">
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">${t['driver-tagliando'] || (lang === 'en' ? 'Next Service' : 'Prossimo Tagliando')}</h3>
                <span class="text-xs font-bold text-white">~${kmToNextService.toLocaleString()} km</span>
            </div>
            <div class="w-full bg-[#1e293b] rounded-full h-2 mb-2 border border-white/5 overflow-hidden">
                <div class="bg-gradient-to-r from-brand-600 to-brand-400 h-2 rounded-full" style="width: ${servicePct}%"></div>
            </div>
            <p class="text-[10px] text-slate-500 text-right">${t['driver-maint-plan'] || (lang === 'en' ? 'Based on the official maintenance plan' : 'Basato sul piano di manutenzione ufficiale')}</p>
        </div>`;
}


function renderGarageList(vehicles, lang, t) {
    if (!vehicles.length) return '';
    const title = lang === 'en' ? 'My Garage' : 'Il mio garage';
    const items = vehicles.map(v => {
        const isPinned = v.is_pinned;
        return `
            <div class="glass-card p-3 mb-2 flex items-center justify-between border ${isPinned ? 'border-brand-500/40' : 'border-white/5'}">
                <div class="flex items-center gap-3 min-w-0 flex-1">
                    ${v.logo_url ? `<img src="${v.logo_url}" onerror="this.style.display='none'" class="w-8 h-8 rounded-md object-contain bg-slate-800 p-1 shrink-0" />` : ''}
                    <div class="min-w-0">
                        <p class="text-sm font-bold text-white truncate">${v.manufacturer} ${v.model}</p>
                        <p class="text-[10px] text-slate-400">${v.plate} · ${v.year || '—'} · ${(v.odometer_km || 0).toLocaleString()} km</p>
                    </div>
                </div>
                <div class="flex items-center gap-1 shrink-0 ml-2">
                    ${isPinned
                        ? '<span class="text-brand-400 text-base" title="Pinned">⭐</span>'
                        : `<button data-action="pin" data-vin="${v.vin}" class="text-[10px] text-slate-500 hover:text-brand-400 px-2 py-1">${lang === 'en' ? 'Pin' : 'Pin'}</button>`}
                    <button data-action="unlink" data-vin="${v.vin}" class="text-[10px] text-slate-500 hover:text-rose-400 px-2 py-1">✕</button>
                </div>
            </div>`;
    }).join('');
    return `
        <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-2 px-1 mt-4">${title}</h3>
        ${items}`;
}


function renderAddVehicleForm(lang, t) {
    return `
        <div class="glass-card p-4 mb-4 border border-white/5">
            <p class="text-xs font-bold text-white mb-2 flex items-center gap-1.5"><span class="text-base">➕</span> ${lang === 'en' ? 'Add Vehicle' : 'Aggiungi veicolo'}</p>
            <div class="flex gap-2">
                <input id="add-vehicle-input" type="text"
                       placeholder="${lang === 'en' ? 'Plate, VIN or policy #' : 'Targa, VIN o n° polizza'}"
                       class="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-brand-500 outline-none"/>
                <button data-action="add-vehicle" class="bg-brand-600 text-black font-bold px-4 py-2 rounded-lg text-sm hover:bg-brand-500 transition-colors">
                    ${lang === 'en' ? 'Link' : 'Collega'}
                </button>
            </div>
        </div>`;
}


function renderMaintenanceForm(v, lang, t) {
    const types = lang === 'en'
        ? [['oil_change', 'Oil change'], ['tire_change', 'Tire change'], ['brake_service', 'Brake service'],
           ['battery_service', 'Battery check'], ['filter_change', 'Filter change'], ['scheduled', 'Scheduled service']]
        : [['oil_change', 'Cambio olio'], ['tire_change', 'Cambio gomme'], ['brake_service', 'Servizio freni'],
           ['battery_service', 'Controllo batteria'], ['filter_change', 'Cambio filtri'], ['scheduled', 'Tagliando programmato']];
    return `
        <div class="glass-card p-4 mb-6 border border-white/5">
            <p class="text-xs font-bold text-white mb-2 flex items-center gap-1.5"><span class="text-base">🔧</span> ${lang === 'en' ? 'Log Maintenance' : 'Registra manutenzione'}</p>
            <select id="maint-type" class="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white mb-2 outline-none">
                ${types.map(([val, lbl]) => `<option value="${val}">${lbl}</option>`).join('')}
            </select>
            <input id="maint-desc" type="text" placeholder="${lang === 'en' ? 'Description (optional)' : 'Descrizione (opzionale)'}"
                   class="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 mb-2 outline-none"/>
            <input id="maint-km" type="number" placeholder="${lang === 'en' ? 'Current mileage (km)' : 'Chilometraggio attuale (km)'}"
                   value="${v.odometer_km || ''}"
                   class="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 mb-2 outline-none"/>
            <button data-action="log-maintenance" data-vin="${v.vin || ''}" class="w-full bg-brand-600 text-black font-bold py-2.5 rounded-lg text-sm hover:bg-brand-500 transition-colors">
                ${lang === 'en' ? 'Save' : 'Salva'}
            </button>
        </div>`;
}


// ── Action handlers (delegated, attached every render) ───────────────────
function wireProfileHandlers() {
    const root = document.getElementById('profile-content-container');
    if (!root) return;

    // PIN
    root.querySelectorAll('[data-action="pin"]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const vin = btn.dataset.vin;
            await fetch(`/api/driver/${DRIVER_ID}/pin/${vin}`, { method: 'PUT' });
            window.showToast && window.showToast('📌 Veicolo aggiornato');
            window.initApp && window.initApp();
        });
    });

    // UNLINK
    root.querySelectorAll('[data-action="unlink"]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const vin = btn.dataset.vin;
            const lang = localStorage.getItem('veritwin_lang') || 'it';
            const msg = lang === 'en' ? 'Remove this vehicle from your garage?' : 'Rimuovere questo veicolo dal garage?';
            if (!confirm(msg)) return;
            await fetch(`/api/driver/${DRIVER_ID}/vehicles/${vin}`, { method: 'DELETE' });
            window.showToast && window.showToast('🚗 Veicolo rimosso');
            window.initApp && window.initApp();
        });
    });

    // ADD VEHICLE
    root.querySelector('[data-action="add-vehicle"]')?.addEventListener('click', async () => {
        const input = root.querySelector('#add-vehicle-input');
        if (!input?.value?.trim()) return;
        const res = await fetch(`/api/driver/${DRIVER_ID}/vehicles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ search: input.value.trim() }),
        });
        const data = await res.json();
        if (data.error) { window.showToast && window.showToast('⚠️ ' + data.error); return; }
        window.showToast && window.showToast('✅ Veicolo aggiunto');
        input.value = '';
        window.initApp && window.initApp();
    });

    // LOG MAINTENANCE
    root.querySelector('[data-action="log-maintenance"]')?.addEventListener('click', async (e) => {
        const vin = e.currentTarget.dataset.vin;
        if (!vin) { window.showToast && window.showToast('Nessun veicolo selezionato'); return; }
        const type = root.querySelector('#maint-type')?.value;
        const desc = root.querySelector('#maint-desc')?.value || '';
        const km   = parseInt(root.querySelector('#maint-km')?.value || '0', 10);
        const lang = localStorage.getItem('veritwin_lang') || 'it';
        await fetch(`/api/driver/${DRIVER_ID}/maintenance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vin, type, description: desc || type, mileage_km: km,
                date: new Date().toISOString().split('T')[0],
            }),
        });
        window.showToast && window.showToast(lang === 'en' ? '✅ Maintenance logged' : '✅ Manutenzione registrata');
        root.querySelector('#maint-desc').value = '';
    });
}
