// static/js/driver/home_view.js

export function renderComponentGrid(components) {
    const container = document.getElementById('component-health-container');
    if (!container) return;

    const lang = localStorage.getItem('veritwin_lang') || 'it';
    const t = (window.translations && window.translations[lang]) || {};

    // Build localized labels from i18n keys
    const labels = {
        'tire_FL': (t['driver-tire'] || 'Tire') + ' FL',
        'tire_FR': (t['driver-tire'] || 'Tire') + ' FR',
        'tire_RL': (t['driver-tire'] || 'Tire') + ' RL',
        'tire_RR': (t['driver-tire'] || 'Tire') + ' RR',
        'brake_pad_front': t['driver-brake-front'] || 'Brake Front',
        'brake_pad_rear': t['driver-brake-rear'] || 'Brake Rear',
        'ev_battery_main': t['driver-ev-battery'] || 'EV Battery'
    };

    const statusLabels = {
        'critical': t['driver-status-critical'] || 'CRITICAL',
        'warning': t['driver-status-warning'] || 'WARNING',
        'good': t['driver-status-good'] || 'GOOD'
    };

    const kmLeftLabel = t['driver-km-left'] || 'km left';

    let html = '<div class="grid grid-cols-2 gap-3">';

    components.forEach(comp => {
        // Create a unique key like "tire_FL"
        const key = `${comp.category}_${comp.position}`;
        const label = labels[key] || comp.category;

        // Default to GOOD (Green)
        let colorClass = "bg-emerald-500";
        let textColor = "text-emerald-500";

        if (comp.urgency === 'critical') {
            colorClass = "bg-red-500";
            textColor = "text-red-500";
        } else if (comp.urgency === 'warning') {
            colorClass = "bg-amber-400"; // Warm yellow/orange
            textColor = "text-amber-400";
        }

        const urgencyLabel = statusLabels[comp.urgency] || comp.urgency;

        html += `
            <div class="glass-card p-3 flex flex-col justify-between border border-white/5 shadow-sm">
                <div class="flex justify-between items-center mb-3">
                    <div class="flex items-center gap-2">
                        <div class="w-2.5 h-2.5 rounded-full ${colorClass} shadow-[0_0_8px_currentColor]"></div>
                        <span class="text-xs font-bold text-white tracking-wide">${label}</span>
                    </div>
                    <span class="text-[9px] font-black ${textColor} uppercase tracking-wider">${urgencyLabel}</span>
                </div>
                <div class="w-full bg-[#1e293b] rounded-full h-1.5 mb-2">
                    <div class="${colorClass} h-1.5 rounded-full" style="width: ${comp.health_pct}%"></div>
                </div>
                <div class="flex justify-between items-end">
                    <span class="text-[9px] font-medium text-slate-400">~${comp.est_remaining_km.toLocaleString()} ${kmLeftLabel}</span>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}