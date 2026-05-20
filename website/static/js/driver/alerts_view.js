export function renderAlertsGrid(components) {
    const alertBadge = document.getElementById('nav-alert-badge');
    const topAlertContainer = document.getElementById('top-alert-container');
    const alertListContainer = document.getElementById('alerts-list-container');

    if (!alertListContainer) return;

    // Grab translations
    const lang = localStorage.getItem('veritwin_lang') || 'it';
    const t = window.translations[lang] || window.translations['it'];

    const issues = components.filter(c => c.urgency !== 'good');
    issues.sort((a, b) => {
        if (a.urgency === 'critical' && b.urgency !== 'critical') return -1;
        if (a.urgency !== 'critical' && b.urgency === 'critical') return 1;
        return a.health_pct - b.health_pct;
    });

    // Fallback dictionary in case agent missed a key
    const labels = {
        'tire_FL': t['driver-tire-fl'] || 'Pneumatico Anteriore Sinistro',
        'tire_FR': t['driver-tire-fr'] || 'Pneumatico Anteriore Destro',
        'tire_RL': t['driver-tire-rl'] || 'Pneumatico Posteriore Sinistro',
        'tire_RR': t['driver-tire-rr'] || 'Pneumatico Posteriore Destro',
        'brake_pad_front': t['driver-brake-front'] || 'Freni Anteriori',
        'brake_pad_rear': t['driver-brake-rear'] || 'Freni Posteriori',
        'ev_battery_main': t['driver-battery'] || 'Batteria EV'
    };

    if (issues.length > 0) {
        alertBadge.classList.remove('hidden');

        // TOP ALERT (Aggressively Scaled down)
        const primaryIssue = issues[0];
        const primaryLabel = labels[`${primaryIssue.category}_${primaryIssue.position}`] || primaryIssue.category;

        if (topAlertContainer) {
            topAlertContainer.innerHTML = `
                <div onclick="window.switchView('view-alert')" class="glass-card p-4 mb-4 border border-brand-500/40 relative overflow-hidden group cursor-pointer shadow-[0_0_15px_rgba(0,229,255,0.05)]">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="flex h-2 w-2 relative"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span></span>
                        <span class="text-[10px] font-bold text-brand-400 uppercase tracking-wider">${t['driver-azione-richiesta'] || 'Azione Richiesta:'} ${primaryLabel}</span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-1">${t['driver-manutenzione-consigliata'] || 'Manutenzione Consigliata'}</h3>
                    <p class="text-xs text-slate-400 line-clamp-2">${
                        primaryIssue.consequence.includes('Battistrada residuo:')
                            ? primaryIssue.consequence.replace('Battistrada residuo:', (t['driver-battistrada-residuo'] || 'Battistrada residuo') + ':')
                            : (t[primaryIssue.consequence === 'Sostituzione consigliata.' ? 'driver-sostituzione-consigliata' : 'driver-batteria-ok'] || primaryIssue.consequence)
                    }</p>
                </div>`;
        }

        // LIST ALERTS (Aggressively Scaled down for mobile)
        let alertsHtml = '';
        issues.forEach(issue => {
            const key = `${issue.category}_${issue.position}`;
            const label = labels[key] || issue.category;
            const isCritical = issue.urgency === 'critical';

            const borderColor = isCritical ? 'border-red-500/50' : 'border-amber-400/50';
            const glowColor = isCritical ? 'shadow-[0_0_10px_rgba(239,68,68,0.05)]' : 'shadow-[0_0_10px_rgba(251,191,36,0.05)]';
            const badgeBg = isCritical ? 'bg-red-600' : 'bg-amber-400';
            const badgeText = isCritical ? 'text-white' : 'text-slate-900';
            const dotColor = isCritical ? 'bg-red-600' : 'bg-amber-500';

            const wearPct = (100 - issue.health_pct).toFixed(1);
            let warningPrefix = isCritical && issue.category === 'brake_pad' ? `<span class="text-amber-400 font-bold">${t['driver-safety-risk'] || '⚠️ SAFETY RISK:'}</span> ` : '';

            // Translated dynamic variables
            const urgencyText = t[`driver-urgency-${issue.urgency}`] || issue.urgency;
            const wearText = t['driver-wear'] || 'Usura';
            const kmText = t['driver-km-left'] || 'km restanti';
            const btnText = t['driver-get-quote'] || 'Richiedi Preventivo';

            // Translate consequence
            let translatedConsequence = issue.consequence;
            if (translatedConsequence.includes('Battistrada residuo:')) {
                translatedConsequence = translatedConsequence.replace('Battistrada residuo:', (t['driver-battistrada-residuo'] || 'Battistrada residuo') + ':');
            } else if (translatedConsequence === 'Sostituzione consigliata.') {
                translatedConsequence = t['driver-sostituzione-consigliata'] || 'Sostituzione consigliata.';
            } else if (translatedConsequence === 'Freni in ottime condizioni.') {
                translatedConsequence = t['driver-freni-ok'] || 'Freni in ottime condizioni.';
            } else if (translatedConsequence === 'Nessuna anomalia termica.') {
                translatedConsequence = t['driver-batteria-ok'] || 'Nessuna anomalia termica.';
            }

            alertsHtml += `
                <div class="glass-card p-3 flex flex-col border ${borderColor} ${glowColor}">
                    <div class="flex justify-between items-center mb-1.5">
                        <div class="flex items-center gap-1.5">
                            <div class="w-2.5 h-2.5 rounded-full ${dotColor} shadow-[0_0_8px_currentColor]"></div>
                            <h3 class="text-sm font-bold text-white tracking-tight">${label}</h3>
                        </div>
                        <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest ${badgeBg} ${badgeText}">
                            ${urgencyText}
                        </span>
                    </div>
                    
                    <p class="text-[11px] text-slate-300 mb-2 leading-snug">
                        ${warningPrefix}${translatedConsequence}
                    </p>
                    
                    <p class="text-[10px] text-slate-500 font-medium mb-3">
                        ${wearText}: <span class="text-white font-bold">${wearPct}%</span> &nbsp;•&nbsp; ~${issue.est_remaining_km.toLocaleString()} ${kmText}
                    </p>
                    
                    <button onclick="window.getRepairQuote('${key}')" class="w-full bg-brand-500 hover:bg-brand-400 text-slate-900 font-bold py-2 rounded-lg transition-all shadow-[0_2px_10px_rgba(0,229,255,0.2)] flex items-center justify-center gap-1.5">
                        <span class="text-sm">💰</span> <span class="text-[13px]">${btnText}</span>
                    </button>
                </div>
            `;
        });
        alertListContainer.innerHTML = alertsHtml;

    } else {
        alertBadge.classList.add('hidden');
        if (topAlertContainer) topAlertContainer.innerHTML = '';
        alertListContainer.innerHTML = `<div class="text-center mt-12"><span class="text-5xl mb-3 block">✅</span><h3 class="text-lg font-bold text-slate-300">${t['driver-nessun-avviso'] || 'Nessun avviso'}</h3></div>`;
    }
}