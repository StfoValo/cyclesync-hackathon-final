// CycleSync Driver App — Main Logic
const DRIVER_ID = 1; // Demo driver
let driverData = null;
let activeVin = null;
let componentData = null;

// Lucide icon helper — returns <i> tag that lucide.createIcons() will render
const luc = (name, cls='w-4 h-4') => `<i data-lucide="${name}" class="${cls}"></i>`;
const refreshIcons = () => { if (window.lucide) setTimeout(() => lucide.createIcons(), 10); };

// ── Component icons (shared design with icons.js) ───────────────────────
const svgTyre = (cls='w-4 h-4') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/><line x1="12" y1="2" x2="12" y2="7"/><line x1="12" y1="17" x2="12" y2="22"/><line x1="2" y1="12" x2="7" y2="12"/><line x1="17" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="8.46" y2="8.46"/><line x1="15.54" y1="15.54" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="15.54" y2="8.46"/><line x1="8.46" y1="15.54" x2="4.93" y2="19.07"/></svg>`;

// Brake pad — two ear mounting tabs (with bolt holes) + curved body with vertical friction grooves
const svgBrakePad = (cls='w-4 h-4') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11 C 3 9.2 4 8.8 5.2 8.8 C 6 8.8 6.6 8.8 7 8.8 C 7 5.8 7.9 4.2 9 4.2 C 10.1 4.2 11 5.8 11 8.8 L 13 8.8 C 13 5.8 13.9 4.2 15 4.2 C 16.1 4.2 17 5.8 17 8.8 C 17.4 8.8 18 8.8 18.8 8.8 C 20 8.8 21 9.2 21 11 L 20.6 14 C 20.2 16.6 18.6 17.2 16.8 17.6 C 13.5 18.4 10.5 18.4 7.2 17.6 C 5.4 17.2 3.8 16.6 3.4 14 Z"/><circle cx="9" cy="6.5" r="0.85"/><circle cx="15" cy="6.5" r="0.85"/><path d="M3.7 11.2 Q12 12.2 20.3 11.2"/><line x1="8" y1="12.5" x2="8" y2="16.7"/><line x1="12" y1="13" x2="12" y2="17.4"/><line x1="16" y1="12.5" x2="16" y2="16.7"/></svg>`;

// Brake disc + caliper — drilled rotor with 5-lug hub + ribbed caliper straddling disc edge
const svgBrakeDisc = (cls='w-4 h-4') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="10" cy="12" r="9"/><circle cx="10" cy="12" r="6.5" opacity="0.55"/><circle cx="10" cy="12" r="2.5"/><circle cx="10" cy="12" r="0.55" fill="currentColor" stroke="none"/><circle cx="10" cy="9.7" r="0.42" fill="currentColor" stroke="none"/><circle cx="12.2" cy="11.3" r="0.42" fill="currentColor" stroke="none"/><circle cx="11.3" cy="14" r="0.42" fill="currentColor" stroke="none"/><circle cx="8.7" cy="14" r="0.42" fill="currentColor" stroke="none"/><circle cx="7.8" cy="11.3" r="0.42" fill="currentColor" stroke="none"/><circle cx="5" cy="8.5" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/><circle cx="14" cy="6" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/><circle cx="6" cy="15.5" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/><circle cx="14" cy="18" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/><circle cx="3.5" cy="12" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/><circle cx="16" cy="12" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/><path d="M14 7 L21.5 7 Q22.5 7 22.5 8 L22.5 16 Q22.5 17 21.5 17 L14 17 Z"/><line x1="16" y1="9" x2="16" y2="15"/><line x1="18" y1="9" x2="18" y2="15"/><line x1="20" y1="9" x2="20" y2="15"/><line x1="22.5" y1="12" x2="23.6" y2="12"/></svg>`;

const svgBattery = (cls='w-4 h-4') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="16" height="10" rx="2"/><path d="M22 11v2"/><path d="M6 11h4M10 9v6"/></svg>`;

// ── Manufacturer Logos (files under /static/img/logos/) ──────────────────
const MFR_LOGO_FILES = new Set([
    'abarth', 'alfa', 'audi', 'bmw', 'dacia', 'ferrari', 'fiat', 'ford',
    'hyundai', 'kia', 'lamborghini', 'maserati', 'mercedes', 'opel', 'peugeot',
    'porsche', 'renault', 'skoda', 'smart', 'tesla', 'toyota', 'volkswagen', 'volvo',
]);

const MFR_ALIASES = {
    'mercedes-benz': 'mercedes',
    'mercedes benz': 'mercedes',
    'vw':            'volkswagen',
    'alfa romeo':    'alfa',
    'alfaromeo':     'alfa',
};

function normalizeMfr(name) {
    if (!name) return '';
    const lower = String(name).toLowerCase().trim();
    if (MFR_ALIASES[lower]) return MFR_ALIASES[lower];
    if (MFR_LOGO_FILES.has(lower)) return lower;
    for (const key of MFR_LOGO_FILES) {
        if (lower.startsWith(key)) return key;
    }
    for (const [alias, target] of Object.entries(MFR_ALIASES)) {
        if (lower.startsWith(alias)) return target;
    }
    return '';
}

function mfrBadge(manufacturer, size='sm') {
    const dimMap = { xs:'w-5 h-5', sm:'w-7 h-7', md:'w-9 h-9', lg:'w-12 h-12' };
    const dim = dimMap[size] || dimMap.sm;
    const key = normalizeMfr(manufacturer);
    if (key) {
        return `<span class="${dim} inline-flex items-center justify-center shrink-0" title="${manufacturer || ''}"><img src="/static/img/logos/${key}.svg?v=17" alt="${manufacturer || ''}" class="w-full h-full object-contain" loading="lazy"/></span>`;
    }
    const initials = (manufacturer || '??').replace(/[^A-Za-z]/g, '').substring(0, 2).toUpperCase();
    return `<span class="${dim} rounded-md flex items-center justify-center font-black tracking-tight bg-slate-700/70 border border-slate-500/40 text-slate-200 text-[10px] shrink-0" title="${manufacturer || ''}">${initials}</span>`;
}

function compIcon(category, cls='w-4 h-4') {
    if (category === 'tire') return svgTyre(cls);
    if (category === 'brake_pad') return svgBrakePad(cls);
    if (category === 'brake_disc') return svgBrakeDisc(cls);
    if (category === 'ev_battery') return svgBattery(cls);
    return luc('settings-2', cls);
}

// ── Init ─────────────────────────────────────────────────────────────────
async function initDriverApp() {
    try {
        const res = await fetch(`/api/driver/${DRIVER_ID}`);
        driverData = await res.json();
        if (driverData.error) { console.error(driverData.error); return; }
        activeVin = driverData.pinned_vin || driverData.vehicles[0]?.vin;
        renderVehicleStrip();
        renderProfileTab();
        await loadVehicleData(activeVin);
    } catch(e) { console.error('Init error:', e); }
}

// ── Vehicle Strip (Home) ─────────────────────────────────────────────────
function renderVehicleStrip() {
    const strip = document.getElementById('vehicle-strip');
    if (!strip || !driverData) return;
    strip.innerHTML = driverData.vehicles.map(v => {
        const active = v.vin === activeVin;
        const badge = mfrBadge(v.manufacturer, 'sm');
        const cls = active
            ? 'bg-brand-600 border-brand-500 text-black shadow-[0_0_15px_rgba(0,229,255,0.3)]'
            : 'bg-slate-800 border-white/10 text-white hover:border-white/20';
        return `<button onclick="selectVehicle('${v.vin}')" class="shrink-0 box-border flex items-center gap-2.5 px-4 h-12 rounded-2xl border ${cls}" style="min-width:180px">
            ${badge}
            <div class="text-left min-w-0">
                <div class="text-xs font-bold leading-tight truncate">${v.manufacturer} ${v.model.replace(v.manufacturer+' ','')}</div>
                <div class="text-[10px] leading-tight ${active?'text-black/60':'text-slate-400'}">${v.plate}${v.is_pinned?` ${luc('star','w-3 h-3 inline')}`:''}</div>
            </div>
        </button>`;
    }).join('');
    refreshIcons();
}

window.selectVehicle = async function(vin) {
    activeVin = vin;
    renderVehicleStrip();
    await loadVehicleData(vin);
};

// ── Load Vehicle Data ────────────────────────────────────────────────────
async function loadVehicleData(vin) {
    const v = driverData.vehicles.find(x => x.vin === vin);
    if (!v) return;
    const cleanModel = v.model.replace(v.manufacturer+' ','');

    // Update top header (small title above vehicle strip)
    const nameEl = document.getElementById('home-vehicle-name');
    if (nameEl) nameEl.textContent = `${v.manufacturer} ${cleanModel}`;
    const plateEl = document.getElementById('home-vehicle-plate');
    if (plateEl) plateEl.textContent = v.plate;

    // Update hero photo card (partner_repo Maserati Grecale-style)
    const photoEl  = document.getElementById('active-vehicle-photo');
    const heroName = document.getElementById('active-vehicle-name');
    const heroPlate= document.getElementById('active-vehicle-plate');
    const heroYear = document.getElementById('active-vehicle-year');
    if (heroName)  heroName.textContent  = `${v.manufacturer} ${cleanModel}`;
    if (heroPlate) heroPlate.textContent = v.plate || '— — —';
    if (heroYear)  heroYear.textContent  = v.year ? `${v.year} · ${v.color || ''}` : (v.color || '—');
    if (photoEl) {
        if (v.photo_url) {
            photoEl.src = v.photo_url;
            photoEl.classList.remove('hidden');
        } else {
            photoEl.classList.add('hidden');
        }
    }

    // VSI
    const vsiEl = document.getElementById('home-vsi-score');
    if (vsiEl) vsiEl.textContent = v.vsi_score || '--';
    const vsiLabel = document.getElementById('home-vsi-label');
    const score = v.vsi_score || 0;
    if (vsiLabel) {
        if (score >= 80) { vsiLabel.textContent = 'Excellent'; vsiLabel.className = 'text-[10px] font-bold text-emerald-400 uppercase'; }
        else if (score >= 60) { vsiLabel.textContent = 'Good'; vsiLabel.className = 'text-[10px] font-bold text-brand-400 uppercase'; }
        else if (score >= 40) { vsiLabel.textContent = 'Fair'; vsiLabel.className = 'text-[10px] font-bold text-amber-400 uppercase'; }
        else { vsiLabel.textContent = 'Poor'; vsiLabel.className = 'text-[10px] font-bold text-rose-400 uppercase'; }
    }
    // VSI ring color
    const ring = document.getElementById('vsi-ring');
    if (ring) ring.style.background = `conic-gradient(${score>=70?'#10b981':score>=40?'#f59e0b':'#ef4444'} ${score*3.6}deg, #1e293b ${score*3.6}deg)`;

    // Telemetry badge
    const bbBadge = document.getElementById('home-bb-badge');
    if (bbBadge) {
        if (v.has_blackbox) { bbBadge.innerHTML = `${luc('satellite-dish','w-3 h-3 inline mr-0.5')} Full Telemetry`; bbBadge.className = 'text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full flex items-center gap-1'; }
        else { bbBadge.innerHTML = `${luc('plug','w-3 h-3 inline mr-0.5')} ECU Only`; bbBadge.className = 'text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full flex items-center gap-1'; }
    }

    // Odometer
    const odoEl = document.getElementById('home-odometer');
    if (odoEl) odoEl.textContent = (v.odometer_km||0).toLocaleString() + ' km';

    // Load component lifecycle
    try {
        const res = await fetch(`/api/driver/vehicle/${vin}/component-life`);
        componentData = await res.json();
        renderComponentHealth(componentData);
        renderAlerts(componentData);
        renderVSITips(componentData.vsi_tips);
        renderDTCAlerts(componentData.dtc_alerts);
    } catch(e) { console.error(e); }
}

// ── Component Health Grid ────────────────────────────────────────────────
function renderComponentHealth(data) {
    const grid = document.getElementById('component-health-grid');
    if (!grid) return;
    const comps = data.components || [];
    if (!comps.length) { grid.innerHTML = '<p class="text-slate-500 text-sm p-4">No components tracked</p>'; return; }

    grid.innerHTML = comps.map(c => {
        const icon = compIcon(c.category, 'w-4 h-4');
        const label = c.category === 'tire' ? `Tire ${c.position}` : c.category === 'brake_pad' ? `Brake ${c.position}` : c.category === 'brake_disc' ? `Disc ${c.position}` : 'EV Battery';
        const wear = c.wear_percent || 0;
        const barColor = c.urgency === 'critical' ? 'bg-rose-500' : c.urgency === 'warning' ? 'bg-amber-500' : 'bg-emerald-500';
        const textColor = c.urgency === 'critical' ? 'text-rose-400' : c.urgency === 'warning' ? 'text-amber-400' : 'text-emerald-400';
        const remKm = c.est_remaining_km?.toLocaleString() || '—';
        return `<div class="glass-card p-3 cursor-pointer hover:border-brand-500/30 transition-all" onclick="this.querySelector('.comp-detail').classList.toggle('hidden')">
            <div class="flex items-center justify-between mb-1.5">
                <span class="text-sm font-semibold text-white flex items-center gap-1.5">${icon} ${label}</span>
                <span class="text-[10px] font-bold ${textColor} uppercase">${c.urgency}</span>
            </div>
            <div class="flex items-center gap-2 mb-1">
                <div class="flex-1 bg-slate-800 rounded-full h-1.5"><div class="${barColor} rounded-full h-1.5" style="width:${wear}%"></div></div>
                <span class="text-xs font-bold ${textColor}">${wear}%</span>
            </div>
            <div class="flex justify-between text-[10px] text-slate-400">
                <span>~${remKm} km left</span>
                <span>${c.brand || ''}</span>
            </div>
            <div class="comp-detail hidden mt-2 pt-2 border-t border-white/5 text-[11px] text-slate-400">
                <p class="mb-1">${c.consequence || 'Normal operation'}</p>
                ${c.est_remaining_days ? `<p>Est. replacement in <span class="text-white font-bold">${c.est_remaining_days}</span> days</p>` : ''}
            </div>
        </div>`;
    }).join('');
    refreshIcons();
}

// ── VSI Tips ─────────────────────────────────────────────────────────────
function renderVSITips(tips) {
    const el = document.getElementById('vsi-tips');
    if (!el || !tips?.length) return;
    el.innerHTML = tips.map(t => `<div class="flex items-start gap-2 mb-1"><span class="text-brand-400 mt-0.5">${luc('lightbulb','w-3.5 h-3.5')}</span><span class="text-slate-300 text-xs">${t}</span></div>`).join('');
    refreshIcons();
}

// ── DTC Alerts ───────────────────────────────────────────────────────────
function renderDTCAlerts(dtcs) {
    const el = document.getElementById('dtc-section');
    if (!el) return;
    if (!dtcs?.length) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    document.getElementById('dtc-list').innerHTML = dtcs.map(d =>
        `<div class="flex items-start gap-2 p-2 bg-amber-500/5 rounded-lg border border-amber-500/20 mb-1">
            <span class="text-amber-400 font-mono text-xs font-bold mt-0.5">${d.code}</span>
            <span class="text-slate-300 text-xs">${d.description}</span>
        </div>`
    ).join('');
}

// ── Alerts Tab ───────────────────────────────────────────────────────────
function renderAlerts(data) {
    const list = document.getElementById('alerts-list');
    if (!list) return;
    const critical = (data.components || []).filter(c => c.urgency !== 'good');
    const dtcs = data.dtc_alerts || [];

    if (!critical.length && !dtcs.length) {
        list.innerHTML = `<div class="text-center py-12 text-slate-500"><div class="flex justify-center mb-2">${luc('circle-check','w-10 h-10 text-emerald-500')}</div><p class="font-semibold">All clear!</p><p class="text-xs">No maintenance alerts</p></div>`;
        refreshIcons();
        return;
    }

    let html = '';
    // Component alerts
    critical.sort((a,b) => (a.urgency==='critical'?0:1) - (b.urgency==='critical'?0:1));
    critical.forEach(c => {
        const icon = compIcon(c.category, 'w-5 h-5');
        const label = c.category === 'tire' ? `Tire ${c.position}` : c.category === 'brake_pad' ? `Brake ${c.position}` : c.category === 'brake_disc' ? `Disc ${c.position}` : 'EV Battery';
        const isCrit = c.urgency === 'critical';
        const borderC = isCrit ? 'border-rose-500/30 bg-rose-500/5' : 'border-amber-500/20 bg-amber-500/5';
        const badgeC = isCrit ? 'bg-rose-500 text-white' : 'bg-amber-500 text-black';
        html += `<div class="glass-card p-4 mb-3 border ${borderC}">
            <div class="flex items-center justify-between mb-2">
                <span class="font-semibold text-white flex items-center gap-2">${icon} ${label}</span>
                <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${badgeC}">${c.urgency}</span>
            </div>
            <p class="text-xs text-slate-400 mb-2">${c.consequence}</p>
            <div class="flex items-center justify-between text-[10px]">
                <span class="text-slate-500">Wear: <span class="text-white font-bold">${c.wear_percent}%</span> · ~${c.est_remaining_km?.toLocaleString()} km left</span>
            </div>
            <button onclick="getRepairQuote('${c.category}','${c.position||''}','${c.brand||''}','${c.wear_percent}')" 
                class="mt-3 w-full bg-brand-600 hover:bg-brand-500 text-black text-xs font-bold py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5">
                ${luc('receipt','w-3.5 h-3.5')} Get Repair Quote
            </button>
        </div>`;
    });
    // DTC alerts
    dtcs.forEach(d => {
        html += `<div class="glass-card p-4 mb-3 border border-amber-500/20 bg-amber-500/5">
            <div class="flex items-center gap-2 mb-1">${luc('triangle-alert','w-4 h-4 text-amber-400')}<span class="font-mono text-amber-400 text-sm font-bold">${d.code}</span></div>
            <p class="text-xs text-slate-300">${d.description}</p>
        </div>`;
    });
    list.innerHTML = html;
    refreshIcons();
}

// ── Repair Quote ─────────────────────────────────────────────────────────
window.getRepairQuote = function(category, position, brand, wear) {
    const modal = document.getElementById('quote-modal');
    const output = document.getElementById('quote-output');
    if (!modal || !output) return;
    modal.classList.remove('hidden');
    const label = category === 'tire' ? `Tire ${position}` : category === 'brake_pad' ? `Brake Pad ${position}` : 'EV Battery';
    
    // AI-estimated pricing
    const prices = {
        'tire': { low: 60, high: 120, labor: 20, name: 'tire replacement' },
        'brake_pad': { low: 40, high: 90, labor: 50, name: 'brake pad replacement' },
        'ev_battery': { low: 2000, high: 8000, labor: 200, name: 'battery service' },
    };
    const p = prices[category] || prices['tire'];
    const partCost = Math.round(p.low + (p.high - p.low) * (parseFloat(wear)/100));
    const total = partCost + p.labor;
    const discount = Math.round(total * 0.08);

    output.innerHTML = `
        <div class="flex justify-center mb-4">${luc('wrench','w-8 h-8 text-brand-400')}</div>
        <h3 class="text-lg font-bold text-white text-center mb-4">AI Repair Estimate</h3>
        <div class="glass-card p-3 mb-3">
            <div class="flex justify-between text-sm mb-1"><span class="text-slate-400">${label} (${brand})</span><span class="text-white font-bold">€${partCost}</span></div>
            <div class="flex justify-between text-sm mb-1"><span class="text-slate-400">Labor</span><span class="text-white font-bold">€${p.labor}</span></div>
            <div class="flex justify-between text-sm pt-2 border-t border-white/10"><span class="text-slate-300 font-semibold">Subtotal</span><span class="text-white font-bold">€${total}</span></div>
        </div>
        <div class="glass-card p-3 mb-3 border border-emerald-500/20 bg-emerald-500/5">
            <div class="flex justify-between text-sm"><span class="text-emerald-400 font-semibold flex items-center gap-1">${luc('ticket','w-4 h-4')} CycleSync Discount</span><span class="text-emerald-400 font-bold">-€${discount}</span></div>
            <div class="flex justify-between text-lg pt-2 border-t border-emerald-500/20 mt-2"><span class="text-white font-bold">Total</span><span class="text-emerald-400 font-bold">€${total - discount}</span></div>
        </div>
        <p class="text-[10px] text-slate-500 text-center mb-3 flex items-center justify-center gap-1">${luc('zap','w-3 h-3')} AI estimate — final price confirmed by mechanic</p>
        <button onclick="switchView('view-map')" class="w-full bg-brand-500 text-black font-bold py-2.5 rounded-xl text-sm">Find Nearest Mechanic →</button>
        <button onclick="document.getElementById('quote-modal').classList.add('hidden')" class="w-full mt-2 bg-transparent border border-white/20 text-slate-300 font-semibold py-2.5 rounded-xl text-sm">Close</button>
    `;
    refreshIcons();
};

// ── SOS ──────────────────────────────────────────────────────────────────
window.triggerSOS = async function() {
    switchView('view-sos');
    const output = document.getElementById('sos-output');
    const statusEl = document.getElementById('sos-status');
    if (!output || !activeVin) return;
    output.innerHTML = '<div class="flex items-center justify-center h-32"><div class="w-8 h-8 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div></div>';
    if (statusEl) statusEl.textContent = 'Analyzing vehicle telemetry...';

    try {
        const lang = localStorage.getItem('veritwin_lang') || 'en';
        const res = await fetch(`/api/ai/sos/${activeVin}?lang=${lang}`);
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        output.innerHTML = '<div id="sos-content"></div>';
        const cd = document.getElementById('sos-content');
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            fullText += decoder.decode(value, { stream: true });
            if (cd) cd.innerHTML = renderMd(fullText);
            output.scrollTop = output.scrollHeight;
        }
        if (statusEl) statusEl.textContent = 'Analysis complete — Help dispatched';
    } catch(e) {
        output.innerHTML = '<p class="text-rose-400 p-4">Connection error. Calling 112...</p>';
    }
};

function renderMd(t) {
    t = t.replace(/### (.*?)(?:\n|$)/g, '<h4 class="text-white font-bold text-base border-b border-white/10 pb-1 mt-4 mb-2">$1</h4>');
    t = t.replace(/## (.*?)(?:\n|$)/g, '<h3 class="text-white font-bold text-lg border-b border-white/10 pb-1 mt-4 mb-2">$1</h3>');
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong class="text-brand-400 font-semibold">$1</strong>');
    t = t.replace(/^\* (.*?)$/gm, '<div class="flex items-start gap-2 mb-1"><span class="text-brand-500">•</span><span class="text-slate-300">$1</span></div>');
    t = t.replace(/\n/g, '<br>');
    return t;
}

// ── Profile Tab ──────────────────────────────────────────────────────────
function renderProfileTab() {
    if (!driverData) return;
    const el = id => document.getElementById(id);
    if (el('profile-name')) el('profile-name').textContent = driverData.display_name;
    if (el('profile-email')) el('profile-email').textContent = driverData.email;
    if (el('profile-phone')) el('profile-phone').textContent = driverData.phone || '—';

    const list = el('profile-vehicles');
    if (!list) return;
    list.innerHTML = driverData.vehicles.map(v => {
        const badge = mfrBadge(v.manufacturer, 'sm');
        return `<div class="glass-card p-3 mb-2 flex items-center justify-between">
            <div class="flex items-center gap-3">
                ${badge}
                <div>
                    <div class="text-sm font-bold text-white">${v.manufacturer} ${v.model.replace(v.manufacturer+' ','')}</div>
                    <div class="text-[10px] text-slate-400">${v.plate} · ${v.year} · ${(v.odometer_km||0).toLocaleString()} km</div>
                </div>
            </div>
            <div class="flex items-center gap-2">
                ${v.is_pinned ? `<span class="text-brand-400">${luc('star','w-4 h-4')}</span>` : `<button onclick="pinVehicle('${v.vin}')" class="text-[10px] text-slate-500 hover:text-brand-400">Pin</button>`}
                <button onclick="unlinkVehicle('${v.vin}')" class="text-[10px] text-slate-500 hover:text-rose-400 ml-1">${luc('x','w-3.5 h-3.5')}</button>
            </div>
        </div>`;
    }).join('');
    refreshIcons();
}

window.pinVehicle = async function(vin) {
    await fetch(`/api/driver/${DRIVER_ID}/pin/${vin}`, { method: 'PUT' });
    location.reload();
};

window.unlinkVehicle = async function(vin) {
    if (!confirm('Remove this vehicle?')) return;
    await fetch(`/api/driver/${DRIVER_ID}/vehicles/${vin}`, { method: 'DELETE' });
    location.reload();
};

window.linkVehicle = async function() {
    const input = document.getElementById('add-vehicle-input');
    if (!input?.value) return;
    const res = await fetch(`/api/driver/${DRIVER_ID}/vehicles`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ search: input.value })
    });
    const data = await res.json();
    if (data.error) { alert(data.error); return; }
    input.value = '';
    location.reload();
};

// ── Log Maintenance ──────────────────────────────────────────────────────
window.logMaintenance = async function() {
    const type = document.getElementById('maint-type')?.value;
    const desc = document.getElementById('maint-desc')?.value;
    const km = document.getElementById('maint-km')?.value;
    if (!type || !activeVin) return;
    await fetch(`/api/driver/${DRIVER_ID}/maintenance`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ vin: activeVin, type, description: desc || type, mileage_km: parseInt(km)||0, date: new Date().toISOString().split('T')[0] })
    });
    alert('Maintenance logged ✓');
    document.getElementById('maint-desc').value = '';
    document.getElementById('maint-km').value = '';
};

// ── View Switching ───────────────────────────────────────────────────────
window.switchView = function(targetId) {
    document.querySelectorAll('.app-view').forEach(v => v.classList.remove('active'));
    document.getElementById(targetId)?.classList.add('active');
    document.querySelectorAll('.nav-btn').forEach(b => { b.classList.remove('text-brand-400'); b.classList.add('text-slate-500'); });
    const map = { 'view-home':'nav-home','view-map':'nav-map','view-alert':'nav-alert','view-profile':'nav-profile' };
    const navId = map[targetId];
    if (navId) { document.getElementById(navId)?.classList.add('text-brand-400'); document.getElementById(navId)?.classList.remove('text-slate-500'); }
};

// Init on load
document.addEventListener('DOMContentLoaded', () => {
    initDriverApp();
    setTimeout(() => { if (window.setLanguage) window.setLanguage(localStorage.getItem('veritwin_lang') || 'en'); }, 50);
});
