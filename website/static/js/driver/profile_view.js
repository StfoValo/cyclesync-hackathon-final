// static/js/driver/profile_view.js

export function renderProfileView(vehicle) {
    const container = document.getElementById('profile-content-container');
    if (!container || !vehicle) return;

    // Grab translations
    const lang = localStorage.getItem('veritwin_lang') || 'it';
    const t = window.translations[lang] || window.translations['it'] || {};

    // Calculate a mock "Next Service"
    const serviceInterval = 20000;
    const currentOdo = vehicle.odometer_km || 0;
    const kmSinceLastService = currentOdo % serviceInterval;
    const kmToNextService = serviceInterval - kmSinceLastService;
    const servicePct = (kmSinceLastService / serviceInterval) * 100;

    // 🛠️ The CSS Linter fix
    const progressBarStyle = `width: ${servicePct}%`;

    const html = `
        <div class="glass-card p-4 mb-4 border border-white/5">
            <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">${t['driver-id-veicolo'] || 'Identità Veicolo'}</h3>
            <div class="grid grid-cols-2 gap-y-4 gap-x-2">
                <div>
                    <p class="text-[10px] text-slate-500 mb-0.5">${t['driver-plate'] || 'Targa'}</p>
                    <p class="text-sm font-bold text-white uppercase">${vehicle.plate || '--'}</p>
                </div>
                <div>
                    <p class="text-[10px] text-slate-500 mb-0.5">${t['driver-year'] || 'Anno'}</p>
                    <p class="text-sm font-bold text-white">${vehicle.year || '--'}</p>
                </div>
                <div class="col-span-2">
                    <p class="text-[10px] text-slate-500 mb-0.5">${t['driver-vin'] || 'VIN (Telaio)'}</p>
                    <p class="text-xs font-mono font-bold text-slate-300 tracking-wider bg-slate-800/50 p-2 rounded-lg border border-white/5 inline-block">${vehicle.vin}</p>
                </div>
            </div>
        </div>

        <div class="glass-card p-4 mb-4 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.05)] relative overflow-hidden group">
            <div class="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none"></div>
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-[11px] font-bold text-emerald-400 uppercase tracking-widest">${t['driver-polizza'] || 'Polizza VeriTwin'}</h3>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">${t['driver-active'] || 'Attiva'}</span>
            </div>
            
            <div class="flex items-end justify-between mb-2">
                <div>
                    <p class="text-[10px] text-slate-400 mb-0.5">${t['driver-expiry'] || 'Scadenza Copertura'}</p>
                    <p class="text-base font-bold text-white">${t['driver-expiry-date'] || '12 Maggio 2027'}</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] text-brand-400 mb-0.5">${t['driver-discount'] || 'Sconto Applicato'}</p>
                    <p class="text-xl font-black text-brand-400">-14%</p>
                </div>
            </div>
        </div>

        <div class="glass-card p-4 mb-4 border border-white/5">
            <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4">${t['driver-servizi'] || 'Servizi Connessi'}</h3>
            
            <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl mb-2 border border-white/5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                    </div>
                    <div>
                        <p class="text-sm font-bold text-white">${t['driver-telepass'] || 'Telepass Europeo'}</p>
                        <p class="text-[10px] text-slate-400">${t['driver-telepass-desc'] || 'Dispositivo associato alla targa'}</p>
                    </div>
                </div>
                <div class="w-8 h-4 bg-blue-500 rounded-full relative cursor-pointer shadow-[0_0_10px_rgba(59,130,246,0.3)]">
                    <div class="absolute right-0.5 top-0.5 w-3 h-3 bg-white rounded-full"></div>
                </div>
            </div>

            <div class="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl border border-white/5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center text-rose-400">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                    </div>
                    <div>
                        <p class="text-sm font-bold text-white">${t['driver-roadside'] || 'Soccorso Stradale'}</p>
                        <p class="text-[10px] text-slate-400">${t['driver-roadside-desc'] || 'Incluso nella polizza'}</p>
                    </div>
                </div>
                <span class="text-xs font-bold text-emerald-400">${t['driver-active-masc'] || 'Attivo'}</span>
            </div>
        </div>

        <div class="glass-card p-4 mb-4 border border-white/5">
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-widest">${t['driver-tagliando'] || 'Prossimo Tagliando'}</h3>
                <span class="text-xs font-bold text-white">~${kmToNextService.toLocaleString()} km</span>
            </div>
            
            <div class="w-full bg-[#1e293b] rounded-full h-2 mb-2 border border-white/5 overflow-hidden">
                <div class="bg-gradient-to-r from-brand-600 to-brand-400 h-2 rounded-full" style="${progressBarStyle}"></div>
            </div>
            
            <p class="text-[10px] text-slate-500 text-right">${t['driver-maint-plan'] || 'Basato sul piano di manutenzione ufficiale'}</p>
        </div>
    `;

    container.innerHTML = html;
}