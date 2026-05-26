// static/js/driver/alerts_view.js
//
// Renders both the top-of-home "next alert" banner AND the full Alerts tab,
// driven by the same components payload that home_view.js consumes.

import { componentIcon } from '/static/js/icons.js?v=18';

const CATEGORY_META = {
    tire:              { label_it: 'Pneumatico',     label_en: 'Tire'         },
    brake_pad:         { label_it: 'Pastiglie',      label_en: 'Brake Pads'   },
    brake_disc:        { label_it: 'Dischi',         label_en: 'Brake Discs'  },
    suspension_damper: { label_it: 'Ammortizzatore', label_en: 'Damper'       },
    aux_12v_battery:   { label_it: 'Batteria 12 V',  label_en: '12 V Battery' },
    engine_oil:        { label_it: 'Olio motore',    label_en: 'Engine Oil'   },
    dpf:               { label_it: 'Filtro DPF',     label_en: 'DPF'          },
    ev_battery:        { label_it: 'Batteria EV',    label_en: 'EV Battery'   },
};

const POSITION_LABELS_IT = {
    FL: 'Ant. Sx', FR: 'Ant. Dx', RL: 'Post. Sx', RR: 'Post. Dx',
    front: 'Anteriori', rear: 'Posteriori', main: '',
};
const POSITION_LABELS_EN = {
    FL: 'Front Left', FR: 'Front Right', RL: 'Rear Left', RR: 'Rear Right',
    front: 'Front', rear: 'Rear', main: '',
};


function labelFor(comp, lang) {
    const meta = CATEGORY_META[comp.category] || { label_it: comp.category, label_en: comp.category, icon: '🔧' };
    const posTable = lang === 'en' ? POSITION_LABELS_EN : POSITION_LABELS_IT;
    const pos = posTable[comp.position] != null ? posTable[comp.position] : (comp.position || '');
    const base = lang === 'en' ? meta.label_en : meta.label_it;
    return pos ? `${base} ${pos}` : base;
}


export function renderAlertsGrid(components) {
    const alertBadge = document.getElementById('nav-alert-badge');
    const topAlertContainer = document.getElementById('top-alert-container');
    const alertListContainer = document.getElementById('alerts-list-container');
    if (!alertListContainer) return;

    const lang = localStorage.getItem('veritwin_lang') || 'it';
    const t = (window.translations && window.translations[lang]) || {};

    const issues = (components || []).filter(c => c.urgency !== 'good');
    issues.sort((a, b) => {
        if (a.urgency === 'critical' && b.urgency !== 'critical') return -1;
        if (a.urgency !== 'critical' && b.urgency === 'critical') return 1;
        return (a.health_pct || 0) - (b.health_pct || 0);
    });

    // ── Bottom-nav red dot + top "Action required" banner ─────────────────
    if (issues.length) {
        if (alertBadge) alertBadge.classList.remove('hidden');
        const primary = issues[0];
        const primaryLabel = labelFor(primary, lang);
        if (topAlertContainer) {
            topAlertContainer.innerHTML = `
                <div onclick="window.switchView('view-alert')"
                     class="glass-card p-4 mb-5 border border-brand-500/40 relative overflow-hidden group cursor-pointer shadow-[0_0_15px_rgba(0,229,255,0.05)]">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="flex h-2 w-2 relative">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
                        </span>
                        <span class="text-[10px] font-bold text-brand-400 uppercase tracking-wider">
                            ${t['driver-azione-richiesta'] || (lang === 'en' ? 'Action required:' : 'Azione richiesta:')} ${primaryLabel}
                        </span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-1">${t['driver-manutenzione-consigliata'] || (lang === 'en' ? 'Recommended Maintenance' : 'Manutenzione consigliata')}</h3>
                    <p class="text-xs text-slate-400 line-clamp-2">${primary.consequence || ''}</p>
                </div>`;
        }
    } else {
        if (alertBadge) alertBadge.classList.add('hidden');
        if (topAlertContainer) topAlertContainer.innerHTML = '';
    }

    // ── Full Alerts list (Avvisi tab) ─────────────────────────────────────
    if (!issues.length) {
        alertListContainer.innerHTML = `
            <div class="text-center mt-12">
                <span class="text-5xl mb-3 block">✅</span>
                <h3 class="text-lg font-bold text-slate-300">${t['driver-nessun-avviso'] || (lang === 'en' ? 'No alerts' : 'Nessun avviso')}</h3>
                <p class="text-xs text-slate-500 mt-1">${lang === 'en' ? 'All components are in good condition.' : 'Tutti i componenti sono in buono stato.'}</p>
            </div>`;
        return;
    }

    const wearText = t['driver-wear'] || (lang === 'en' ? 'Wear' : 'Usura');
    const kmText   = t['driver-km-left'] || (lang === 'en' ? 'km left' : 'km restanti');
    const btnText  = t['driver-get-quote'] || (lang === 'en' ? 'Get Repair Quote' : 'Richiedi Preventivo');

    alertListContainer.innerHTML = issues.map(issue => {
        const label = labelFor(issue, lang);
        const key = `${issue.category}_${issue.position || 'main'}`;
        const isCritical = issue.urgency === 'critical';
        const borderColor = isCritical ? 'border-red-500/50'      : 'border-amber-400/50';
        const glowColor   = isCritical ? 'shadow-[0_0_10px_rgba(239,68,68,0.05)]' : 'shadow-[0_0_10px_rgba(251,191,36,0.05)]';
        const badgeBg     = isCritical ? 'bg-red-600'             : 'bg-amber-400';
        const badgeText   = isCritical ? 'text-white'             : 'text-slate-900';
        const dotColor    = isCritical ? 'bg-red-600'             : 'bg-amber-500';
        const iconColor   = isCritical ? 'text-red-400'           : 'text-amber-300';
        const wear = (issue.wear_percent != null) ? issue.wear_percent.toFixed(1) : (100 - issue.health_pct).toFixed(1);
        const safetyPrefix = (isCritical && (issue.category === 'brake_pad' || issue.category === 'brake_disc'))
            ? `<span class="text-amber-400 font-bold">${t['driver-safety-risk'] || (lang === 'en' ? '⚠️ SAFETY RISK:' : '⚠️ RISCHIO:')}</span> ` : '';
        const urgencyText = t[`driver-urgency-${issue.urgency}`] || issue.urgency.toUpperCase();
        const iconSvg = componentIcon(issue.category, `w-5 h-5 ${iconColor}`);
        return `
            <div class="glass-card p-3 flex flex-col border ${borderColor} ${glowColor}">
                <div class="flex justify-between items-center mb-1.5">
                    <div class="flex items-center gap-1.5">
                        <div class="w-2.5 h-2.5 rounded-full ${dotColor} shadow-[0_0_8px_currentColor]"></div>
                        ${iconSvg}
                        <h3 class="text-sm font-bold text-white tracking-tight">${label}</h3>
                    </div>
                    <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest ${badgeBg} ${badgeText}">${urgencyText}</span>
                </div>
                <p class="text-[11px] text-slate-300 mb-1 leading-snug">${safetyPrefix}${issue.consequence || ''}</p>
                ${issue.brand ? `<p class="text-[10px] text-slate-500 mb-1">${issue.brand}${issue.model ? ' · ' + issue.model : ''}</p>` : ''}
                ${issue.ai_reasoning ? `<p class="text-[9px] italic text-slate-500 mb-2">${issue.ai_reasoning}</p>` : ''}
                <p class="text-[10px] text-slate-500 font-medium mb-3">
                    ${wearText}: <span class="text-white font-bold">${wear}%</span> · ~${(issue.est_remaining_km || 0).toLocaleString()} ${kmText}
                </p>
                <button onclick="window.getRepairQuote('${key}')"
                        class="w-full bg-brand-500 hover:bg-brand-400 text-slate-900 font-bold py-2 rounded-lg transition-all shadow-[0_2px_10px_rgba(0,229,255,0.2)] flex items-center justify-center gap-1.5">
                    <span class="text-sm">💰</span> <span class="text-[13px]">${btnText}</span>
                </button>
            </div>`;
    }).join('');
}
