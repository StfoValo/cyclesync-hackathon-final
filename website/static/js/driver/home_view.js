// static/js/driver/home_view.js
//
// Renders the consumer driver app's Home tab:
//   • component health grid (8 categories from the new ESG seeder)
//   • conic-gradient VSI ring + label
//   • expandable VSI improvement tips
//   • DTC alerts (auto-shown when telemetry has active codes)

import { componentIcon } from '/static/js/icons.js?v=18';

// Per-category metadata: localised label (kept short for the 2-col grid).
// The SVG icon is fetched from icons.js#componentIcon(category) so we stay
// consistent with the OEM dashboard.
const CATEGORY_META = {
    tire:              { label_it: 'Pneumatico',    label_en: 'Tire'         },
    brake_pad:         { label_it: 'Pastiglie',     label_en: 'Brake Pads'   },
    brake_disc:        { label_it: 'Dischi',        label_en: 'Brake Discs'  },
    suspension_damper: { label_it: 'Ammortizzatore',label_en: 'Damper'       },
    aux_12v_battery:   { label_it: 'Batteria 12 V', label_en: '12 V Battery' },
    engine_oil:        { label_it: 'Olio motore',   label_en: 'Engine Oil'   },
    dpf:               { label_it: 'Filtro DPF',    label_en: 'DPF'          },
    ev_battery:        { label_it: 'Batteria EV',   label_en: 'EV Battery'   },
};

const POSITION_SHORT = {
    FL: 'AS', FR: 'AD', RL: 'PS', RR: 'PD',          // IT abbreviations
    front: 'Ant.', rear: 'Post.',
    main: '',
};
const POSITION_SHORT_EN = {
    FL: 'FL', FR: 'FR', RL: 'RL', RR: 'RR',
    front: 'Front', rear: 'Rear', main: '',
};


function labelFor(comp, lang) {
    const meta = CATEGORY_META[comp.category] || { label_it: comp.category, label_en: comp.category, icon: '🔧' };
    const posTable = lang === 'en' ? POSITION_SHORT_EN : POSITION_SHORT;
    const pos = posTable[comp.position] != null ? posTable[comp.position] : (comp.position || '');
    const base = lang === 'en' ? meta.label_en : meta.label_it;
    return pos ? `${base} ${pos}` : base;
}


export function renderComponentGrid(components) {
    const container = document.getElementById('component-health-container');
    if (!container) return;

    const lang = localStorage.getItem('veritwin_lang') || 'it';
    const t = (window.translations && window.translations[lang]) || {};

    const statusLabels = {
        critical: t['driver-status-critical'] || (lang === 'en' ? 'CRITICAL' : 'CRITICO'),
        warning:  t['driver-status-warning']  || (lang === 'en' ? 'WARNING'  : 'ATTENZIONE'),
        good:     t['driver-status-good']     || (lang === 'en' ? 'GOOD'     : 'OK'),
    };
    const kmLeftLabel = t['driver-km-left'] || (lang === 'en' ? 'km left' : 'km restanti');

    if (!components || !components.length) {
        container.innerHTML = `<div class="text-slate-500 text-sm text-center py-6">${lang === 'en' ? 'No components tracked.' : 'Nessun componente tracciato.'}</div>`;
        return;
    }

    // Group + render in a stable category order so the grid stays predictable.
    const ORDER = ['tire', 'brake_pad', 'brake_disc', 'suspension_damper',
                   'aux_12v_battery', 'engine_oil', 'dpf', 'ev_battery'];
    const sorted = [...components].sort((a, b) => {
        const ia = ORDER.indexOf(a.category); const ib = ORDER.indexOf(b.category);
        if (ia !== ib) return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
        const pa = (a.position || ''); const pb = (b.position || '');
        return pa.localeCompare(pb);
    });

    const cards = sorted.map(comp => {
        const label = labelFor(comp, lang);
        let dotColor = 'bg-emerald-500', textColor = 'text-emerald-500';
        let iconColor = 'text-emerald-400';
        if (comp.urgency === 'critical') {
            dotColor = 'bg-red-500';   textColor = 'text-red-500';   iconColor = 'text-red-400';
        } else if (comp.urgency === 'warning') {
            dotColor = 'bg-amber-400'; textColor = 'text-amber-400'; iconColor = 'text-amber-400';
        }
        const urgencyLabel = statusLabels[comp.urgency] || (comp.urgency || '').toUpperCase();
        const key = `${comp.category}_${comp.position || 'main'}`;
        const iconSvg = componentIcon(comp.category, `w-4 h-4 ${iconColor}`);
        return `
            <div class="glass-card p-3 flex flex-col border border-white/5 shadow-sm cursor-pointer hover:border-brand-500/30 transition-all"
                 onclick="this.querySelector('.comp-detail').classList.toggle('hidden')">
                <div class="flex justify-between items-center mb-2">
                    <div class="flex items-center gap-1.5">
                        ${iconSvg}
                        <span class="text-[11px] font-bold text-white tracking-tight">${label}</span>
                    </div>
                    <span class="text-[9px] font-black ${textColor} uppercase tracking-wider">${urgencyLabel}</span>
                </div>
                <div class="w-full bg-[#1e293b] rounded-full h-1.5 mb-1.5 border border-white/5">
                    <div class="${dotColor} h-1.5 rounded-full transition-all" style="width: ${comp.health_pct}%"></div>
                </div>
                <div class="flex justify-between items-center text-[9px] text-slate-400">
                    <span>~${(comp.est_remaining_km || 0).toLocaleString()} ${kmLeftLabel}</span>
                    <span class="text-slate-500 truncate max-w-[80px]">${comp.brand || ''}</span>
                </div>
                <div class="comp-detail hidden mt-2 pt-2 border-t border-white/5 text-[10px] text-slate-400 leading-relaxed">
                    <p class="text-slate-300 mb-1">${comp.consequence || ''}</p>
                    ${comp.ai_reasoning ? `<p class="text-[9px] italic text-slate-500 mb-2">${comp.ai_reasoning}</p>` : ''}
                    ${comp.urgency !== 'good' ? `<button onclick="event.stopPropagation(); window.getRepairQuote && window.getRepairQuote('${key}')"
                        class="w-full bg-brand-500 hover:bg-brand-400 text-slate-900 font-bold py-1.5 rounded-md transition-all text-[11px] flex items-center justify-center gap-1.5 mt-1">
                        💰 ${lang === 'en' ? 'Get Repair Quote' : 'Richiedi Preventivo'}
                    </button>` : ''}
                </div>
            </div>`;
    }).join('');

    container.innerHTML = `<div class="grid grid-cols-2 gap-3">${cards}</div>`;
}


export function renderVsiRing(score) {
    const ring = document.getElementById('vsi-ring');
    const label = document.getElementById('vsi-label');
    const scoreEl = document.getElementById('active-vehicle-vsi');
    const s = (score != null) ? Math.max(0, Math.min(100, score)) : 0;
    if (scoreEl) scoreEl.textContent = score ?? '--';
    if (ring) {
        const color = s >= 70 ? '#10b981' : s >= 40 ? '#f59e0b' : '#ef4444';
        ring.style.background = `conic-gradient(${color} ${s * 3.6}deg, #1e293b ${s * 3.6}deg)`;
    }
    if (label) {
        const lang = localStorage.getItem('veritwin_lang') || 'it';
        if (s >= 80) { label.textContent = lang === 'en' ? 'Excellent' : 'Eccellente'; label.className = 'text-[10px] font-bold text-emerald-400 uppercase'; }
        else if (s >= 60) { label.textContent = lang === 'en' ? 'Good' : 'Buono';      label.className = 'text-[10px] font-bold text-brand-400 uppercase'; }
        else if (s >= 40) { label.textContent = lang === 'en' ? 'Fair' : 'Discreto';   label.className = 'text-[10px] font-bold text-amber-400 uppercase'; }
        else              { label.textContent = lang === 'en' ? 'Poor' : 'Insufficiente'; label.className = 'text-[10px] font-bold text-rose-400 uppercase'; }
    }
}


export function renderVsiTips(tips) {
    const el = document.getElementById('vsi-tips');
    if (!el) return;
    if (!tips || !tips.length) { el.innerHTML = ''; return; }
    el.innerHTML = tips.map(t =>
        `<div class="flex items-start gap-2 mb-1.5">
            <span class="text-brand-400 mt-0.5">💡</span>
            <span class="text-slate-300 text-xs leading-snug">${t}</span>
        </div>`
    ).join('');
}


export function renderDtcAlerts(dtcs) {
    const sect = document.getElementById('dtc-section');
    const list = document.getElementById('dtc-list');
    if (!sect || !list) return;
    if (!dtcs || !dtcs.length) { sect.classList.add('hidden'); list.innerHTML = ''; return; }
    sect.classList.remove('hidden');
    list.innerHTML = dtcs.map(d => {
        const sev = d.severity === 'pending' ? 'text-slate-400 bg-slate-500/10' : 'text-amber-400 bg-amber-500/10';
        const sevLabel = d.severity === 'pending' ? 'PENDING' : 'ACTIVE';
        return `<div class="flex items-start gap-2 p-2 bg-amber-500/5 rounded-lg border border-amber-500/20 mb-1.5">
            <span class="font-mono text-xs font-bold text-amber-400 mt-0.5 shrink-0">${d.code}</span>
            <div class="flex-1 min-w-0">
                <p class="text-slate-300 text-xs">${d.description}</p>
                <p class="text-[9px] font-bold ${sev} px-1.5 py-0.5 rounded inline-block mt-1">${sevLabel}</p>
            </div>
        </div>`;
    }).join('');
}
