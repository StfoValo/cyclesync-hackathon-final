/**
 * Adjuster Portal — Investigation list → detail workflow
 * Backed by /api/db/investigations endpoints
 */
import { incidentIcon, componentIcon, iconBrakeDisc, manufacturerBadge } from '/static/js/icons.js?v=18';
import { renderCategorizedTelemetry } from './telemetry_panel.js?v=4';

let currentInvestigation = null;

export function initAdjuster() {
    loadInvestigationList();
    setupFilterPills();
    setupBackButton();
    setupDetailTabs();
    setupVerdictButtons();
    setupAIAnalysis();
    setupPhotoUpload();
}

// ── LIST VIEW ────────────────────────────────────────────────────────────
async function loadInvestigationList(statusFilter = '') {
    const container = document.getElementById('investigation-list');
    if (!container) return;
    container.innerHTML = '<div class="text-center py-8 text-slate-500">Loading investigations...</div>';

    try {
        const params = statusFilter ? `?status=${statusFilter}` : '';
        const resp = await fetch(`/api/db/investigations${params}`);
        const investigations = await resp.json();
        renderInvestigationList(investigations);
    } catch (e) {
        container.innerHTML = '<div class="text-center py-8 text-rose-400">Failed to load investigations</div>';
    }
}

function renderInvestigationList(investigations) {
    const container = document.getElementById('investigation-list');
    if (!investigations?.length) {
        container.innerHTML = '<div class="text-center py-8 text-slate-500">No investigations found</div>';
        return;
    }

    container.innerHTML = investigations.map(inv => {
        const statusColors = {
            open: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
            under_review: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            resolved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
        };
        const priorityColors = {
            critical: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
            high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
            medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            low: 'bg-slate-500/20 text-slate-400 border-slate-500/30'
        };
        // Map type → icon + label
        const typeConfig = {
            collision:   { label: 'Collision',    cls: 'text-rose-400' },
            rear_end:    { label: 'Rear-End',     cls: 'text-orange-400' },
            side_impact: { label: 'Side Impact',  cls: 'text-amber-400' },
            rollover:    { label: 'Rollover',     cls: 'text-purple-400' },
            pedestrian:  { label: 'Pedestrian',   cls: 'text-blue-400' },
        };
        const tc = typeConfig[inv.incident_type] || { label: inv.incident_type, cls: 'text-slate-400' };
        const typeHtml = `<span class="inline-flex items-center gap-1 ${tc.cls}">${incidentIcon(inv.incident_type, 'w-3.5 h-3.5')} ${tc.label}</span>`;
        const fraudColor = inv.fraud_risk_score >= 70 ? 'text-rose-400' : inv.fraud_risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400';
        const statusBadge = statusColors[inv.status] || statusColors.open;
        const priorityBadge = priorityColors[inv.priority] || priorityColors.medium;

        return `
        <div class="investigation-card glass-panel rounded-xl p-4 md:p-5 border border-white/5 hover:border-white/15 cursor-pointer transition-all hover:shadow-lg group" data-case="${inv.case_number}">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                <div class="flex-1">
                    <div class="flex flex-wrap items-center gap-2 mb-2">
                        <span class="font-bold text-white text-sm whitespace-nowrap">${inv.case_number}</span>
                        <span class="text-xs px-2 py-0.5 rounded-full border font-medium whitespace-nowrap ${statusBadge}">${inv.status?.replace('_',' ')}</span>
                        <span class="text-xs px-2 py-0.5 rounded-full border font-medium ${priorityBadge}">${inv.priority}</span>
                    </div>
                    <div class="flex flex-wrap items-center gap-3">
                        <span class="font-mono font-bold text-white text-xs bg-black/40 px-2 py-1 rounded border border-slate-700">${inv.plate_number}</span>
                        <span class="inline-flex items-center gap-2 text-sm text-slate-300">
                            ${manufacturerBadge(inv.manufacturer, 'sm')}
                            <span>${inv.manufacturer} ${inv.model_name}</span>
                        </span>
                        <span class="text-xs text-slate-500">${typeHtml}</span>
                        <span class="text-xs text-slate-500">${inv.incident_date}</span>
                    </div>
                    <p class="text-xs text-slate-400 mt-2 line-clamp-1">${inv.incident_description || ''}</p>
                </div>
                <div class="flex items-center gap-5 shrink-0">
                    <div class="text-center">
                        <div class="text-xl font-black ${fraudColor}">${inv.fraud_risk_score}%</div>
                        <div class="text-[10px] text-slate-500 uppercase">Fraud Risk</div>
                    </div>
                    <div class="text-center">
                        <div class="text-lg font-bold text-white">${inv.speed_at_impact || '—'}<span class="text-xs text-slate-400 ml-1">km/h</span></div>
                        <div class="text-[10px] text-slate-500 uppercase">Speed</div>
                    </div>
                    <div class="text-center">
                        <div class="text-lg font-bold text-white">${inv.g_force_max || '—'}<span class="text-xs text-slate-400 ml-1">G</span></div>
                        <div class="text-[10px] text-slate-500 uppercase">G-Force</div>
                    </div>
                    <svg class="w-5 h-5 text-slate-600 group-hover:text-brand-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </div>
            </div>
        </div>`;
    }).join('');

    // Wire card clicks
    container.querySelectorAll('.investigation-card').forEach(card => {
        card.addEventListener('click', () => openInvestigation(card.getAttribute('data-case')));
    });
}

function setupFilterPills() {
    document.querySelectorAll('.adj-filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.adj-filter-btn').forEach(b => {
                b.classList.remove('bg-brand-600', 'text-white', 'border-brand-500/50');
                b.classList.add('text-slate-400', 'border-slate-700');
            });
            btn.classList.add('bg-brand-600', 'text-white', 'border-brand-500/50');
            btn.classList.remove('text-slate-400', 'border-slate-700');
            loadInvestigationList(btn.getAttribute('data-status'));
        });
    });
}

// ── DETAIL VIEW ──────────────────────────────────────────────────────────
async function openInvestigation(caseNumber) {
    try {
        const resp = await fetch(`/api/db/investigations/${encodeURIComponent(caseNumber)}`);
        const data = await resp.json();
        if (data.error) return;
        currentInvestigation = data;
        renderInvestigationDetail(data);
        document.getElementById('adjuster-list-view')?.classList.add('hidden');
        document.getElementById('adjuster-detail-view')?.classList.remove('hidden');
    } catch (e) { console.error('Failed to load investigation:', e); }
}

function renderInvestigationDetail(inv) {
    // Header
    document.getElementById('detail-case-number').textContent = inv.case_number;

    const statusColors = {open:'bg-rose-500/20 text-rose-400 border border-rose-500/30', under_review:'bg-amber-500/20 text-amber-400 border border-amber-500/30', resolved:'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'};
    const sb = document.getElementById('detail-status-badge');
    sb.textContent = inv.status?.replace('_',' ');
    sb.className = `text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[inv.status] || ''}`;

    const prioColors = {critical:'bg-rose-500/20 text-rose-400 border border-rose-500/30', high:'bg-orange-500/20 text-orange-400 border border-orange-500/30', medium:'bg-amber-500/20 text-amber-400 border border-amber-500/30'};
    const pb = document.getElementById('detail-priority-badge');
    pb.textContent = `${inv.priority}`;
    pb.className = `text-xs px-2 py-0.5 rounded-full font-medium ${prioColors[inv.priority] || ''}`;

    document.getElementById('detail-vehicle').textContent = inv.plate_number;
    document.getElementById('detail-model').innerHTML = `<span class="inline-flex items-center gap-2">${manufacturerBadge(inv.manufacturer, 'sm')}<span>${inv.manufacturer} ${inv.model_name} · ${inv.driver_name || ''}</span></span>`;
    document.getElementById('detail-date').textContent = inv.incident_date;

    const fraudColor = inv.fraud_risk_score >= 70 ? 'text-rose-400 animate-pulse' : inv.fraud_risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400';
    document.getElementById('detail-fraud-score').className = `text-3xl font-black ${fraudColor}`;
    document.getElementById('detail-fraud-score').textContent = `${inv.fraud_risk_score}%`;
    document.getElementById('detail-speed').textContent = `${inv.speed_at_impact || '—'} km/h`;
    document.getElementById('detail-gforce').textContent = `${inv.g_force_max || '—'} G`;

    // Summary tab
    const typeConfig = {
        collision:   { label: 'Collision',   cls: 'text-rose-400' },
        rear_end:    { label: 'Rear-End',    cls: 'text-orange-400' },
        side_impact: { label: 'Side Impact', cls: 'text-amber-400' },
    };
    const tc = typeConfig[inv.incident_type] || { label: inv.incident_type, cls: 'text-slate-400' };
    document.getElementById('detail-incident-type').innerHTML = `<span class="inline-flex items-center gap-1.5 ${tc.cls}">${incidentIcon(inv.incident_type, 'w-4 h-4')} ${tc.label}</span>`;
    document.getElementById('detail-location').textContent = inv.incident_location || '—';
    document.getElementById('detail-description').textContent = inv.incident_description || '—';

    document.getElementById('detail-abs').innerHTML = inv.abs_triggered ? '<span class="text-rose-400 font-semibold">YES</span>' : '<span class="text-emerald-400">No</span>';
    document.getElementById('detail-airbag').innerHTML = inv.airbag_deployed ? '<span class="text-rose-400 font-semibold">DEPLOYED</span>' : '<span class="text-emerald-400">Not deployed</span>';
    document.getElementById('detail-glateral').textContent = `${inv.g_force_lateral || '—'} G`;
    const ct = inv.coolant_temp;
    document.getElementById('detail-coolant').innerHTML = ct ? `<span class="${ct > 95 ? 'text-rose-400' : 'text-emerald-400'}">${ct}°C</span>` : '—';

    // TPMS
    const tpms = inv.tpms_snapshot || {};
    document.getElementById('detail-tpms').innerHTML = ['fl','fr','rl','rr'].map(p => {
        const v = tpms[p];
        const c = v == null ? 'text-slate-500' : v < 2.0 ? 'text-rose-400' : v < 2.2 ? 'text-amber-400' : 'text-emerald-400';
        return `<div class="bg-slate-800/50 rounded-lg p-3 border border-white/5 text-center"><div class="text-xs text-slate-500 mb-1">${p.toUpperCase()}</div><div class="font-bold ${c}">${v?.toFixed(2) ?? '—'}</div></div>`;
    }).join('');

    // Telemetry tab
    renderDetailTelemetry(inv.case_number, inv.telemetry);

    // Components tab
    renderDetailComponents(inv.components || []);

    // AI Analysis
    const repairCost = inv.ai_repair_estimate_eur;
    document.getElementById('detail-repair-cost').textContent = repairCost ? `€${repairCost.toLocaleString()}` : '—';
    if (inv.ai_fraud_analysis) document.getElementById('detail-ai-fraud').innerHTML = `<p class="text-slate-300 text-sm leading-relaxed">${inv.ai_fraud_analysis}</p>`;
    if (inv.ai_verdict) document.getElementById('detail-verdict-content').innerHTML = `<p class="text-xl font-bold text-white mb-2">${inv.ai_verdict}</p>`;

    // Load photos
    loadPhotos(inv.case_number);

    // Show first tab
    showTab('summary');
}

async function renderDetailTelemetry(caseNumber, fallbackTel) {
    const outerGrid = document.getElementById('detail-telemetry-grid');
    if (!outerGrid) return;

    outerGrid.innerHTML = '<div class="col-span-2 md:col-span-4 text-center text-slate-500 py-6 text-sm">Loading locked telemetry window…</div>';

    // Try to fetch the ±5-min locked window first.
    let data = null;
    try {
        const r = await fetch(`/api/db/investigations/${encodeURIComponent(caseNumber)}/telemetry-samples`);
        if (r.ok) data = await r.json();
    } catch (_) { /* ignore — fall back below */ }

    // Fallback: no samples recorded for this case → render the live post-crash snapshot.
    if (!data || !Array.isArray(data.samples) || !data.samples.length) {
        renderCategorizedTelemetry(outerGrid, fallbackTel, {});
        return;
    }

    const samples   = data.samples;
    const events    = data.events || [];
    const impactIdx = samples.findIndex(s => s.seconds_relative === 0);
    let currentIdx  = impactIdx >= 0 ? impactIdx : Math.floor(samples.length / 2);

    // Build the LOCKED panel structure once. The scrubber + event chips
    // stay across redraws; only the time label, stamp, and `#adj-tel-inner`
    // body get repainted on each scrubber tick — preserves slider focus.
    outerGrid.innerHTML = `
        <div class="col-span-2 md:col-span-4">
            <div class="mb-3 px-3 py-2 bg-rose-500/10 border border-rose-500/30 rounded-lg flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <span class="text-rose-400 text-lg">🔒</span>
                    <div>
                        <div class="text-xs font-bold text-rose-300 uppercase tracking-wider">Locked Evidence Window</div>
                        <div class="text-[10px] text-rose-300/70">±5 min around impact · 5 s resolution · ${samples.length} samples</div>
                    </div>
                </div>
                <div class="text-right">
                    <div id="adj-tel-time-label" class="text-lg font-black text-white leading-tight">—</div>
                    <div id="adj-tel-stamp" class="text-[10px] text-slate-500 font-mono">—</div>
                </div>
            </div>

            <div class="mb-2">
                <input type="range" id="adj-tel-scrubber" min="0" max="${samples.length - 1}" value="${currentIdx}"
                    class="w-full accent-rose-500 cursor-pointer">
                <div class="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                    <span>T −5:00</span><span>T −2:30</span>
                    <span class="text-rose-400">T 0 · IMPACT</span>
                    <span>T +2:30</span><span>T +5:00</span>
                </div>
            </div>

            ${events.length ? `<div class="flex flex-wrap gap-1.5 mb-4">
                ${events.map(e => {
                    const seq = samples.findIndex(s => s.seconds_relative === e.sec_relative);
                    const isImpact = e.tag.includes('IMPACT') || e.tag.includes('FCW');
                    const isAirbag = e.tag.includes('airbag');
                    const isAbs    = e.tag.includes('abs') || e.tag.includes('esc');
                    const cls = isImpact ? 'bg-rose-500/20 border-rose-500/50 text-rose-300'
                              : isAirbag ? 'bg-orange-500/20 border-orange-500/40 text-orange-300'
                              : isAbs    ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                              : 'bg-slate-700/40 border-white/10 text-slate-300';
                    const sign = e.sec_relative >= 0 ? '+' : '';
                    return `<button data-seq="${seq}" class="adj-tel-event-btn text-[10px] px-2 py-1 rounded border ${cls} hover:brightness-125 transition-all font-mono">
                        ${sign}${e.sec_relative}s · ${e.tag}
                    </button>`;
                }).join('')}
            </div>` : ''}

            <div id="adj-tel-inner" class="grid grid-cols-2 md:grid-cols-4 gap-3"></div>
        </div>`;

    const inner     = document.getElementById('adj-tel-inner');
    const timeLabel = document.getElementById('adj-tel-time-label');
    const stamp     = document.getElementById('adj-tel-stamp');

    function fmtT(s) {
        if (s === 0) return 'T = 0 · IMPACT';
        const m = Math.floor(Math.abs(s) / 60);
        const r = Math.abs(s) % 60;
        const sign = s < 0 ? '−' : '+';
        return m ? `T ${sign}${m}:${String(r).padStart(2,'0')}` : `T ${sign}${r} s`;
    }

    function paint(idx) {
        const s = samples[idx];
        const tStr = fmtT(s.seconds_relative);
        const flag = (s.event_flag && s.event_flag !== 'normal') ? s.event_flag : '';
        timeLabel.innerHTML = `${tStr}${flag ? ` <span class="text-[11px] text-rose-400">· ${flag}</span>` : ''}`;
        timeLabel.className = 'text-lg font-black leading-tight ' + (s.seconds_relative === 0 ? 'text-rose-400 animate-pulse' : 'text-white');
        stamp.textContent = s.sample_time ? new Date(s.sample_time).toLocaleString() : '—';
        renderCategorizedTelemetry(inner, { vin: 'incident-window', ...s }, {});
    }

    paint(currentIdx);

    document.getElementById('adj-tel-scrubber').addEventListener('input', (e) => {
        currentIdx = parseInt(e.target.value, 10);
        paint(currentIdx);
    });

    document.querySelectorAll('.adj-tel-event-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const seq = parseInt(btn.dataset.seq, 10);
            if (!Number.isNaN(seq) && seq >= 0) {
                currentIdx = seq;
                document.getElementById('adj-tel-scrubber').value = seq;
                paint(currentIdx);
            }
        });
    });
}

function renderDetailComponents(components) {
    const grid = document.getElementById('detail-components-grid');
    if (!components?.length) { grid.innerHTML = '<div class="text-slate-500">No component data</div>'; return; }

    grid.innerHTML = components.map(c => {
        const wear = c.wear_percent || 0;
        const health = 100 - wear;
        const status = c.health_status || (wear > 80 ? 'critical' : wear > 60 ? 'warning' : 'healthy');
        const color = status === 'critical' ? 'text-rose-400' : status === 'warning' ? 'text-amber-400' : 'text-emerald-400';
        const barColor = status === 'critical' ? 'bg-rose-500' : status === 'warning' ? 'bg-amber-500' : 'bg-emerald-500';
        const borderColor = status === 'critical' ? 'border-rose-500/30' : status === 'warning' ? 'border-amber-500/30' : 'border-emerald-500/30';
        const catLabels = {tire:'Tire', brake_pad:'Brake Pad', ev_battery:'Battery', brake_disc:'Brake Disc'};
        const catIcon = componentIcon(c.category, 'w-4 h-4 inline-block mr-1');

        return `<div class="bg-slate-800/50 rounded-lg p-4 border ${borderColor}">
            <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-white flex items-center gap-1.5">${catIcon} ${catLabels[c.category] || c.category} ${c.position ? `(${c.position})` : ''}</span>
                <span class="text-xs font-bold ${color} uppercase">${status}</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-1.5 mb-2"><div class="${barColor} rounded-full h-1.5" style="width:${health}%"></div></div>
            <div class="text-xs text-slate-400">${c.brand || ''} ${c.model_name || ''} · ${health}% health</div>
        </div>`;
    }).join('');
}

function setupBackButton() {
    document.getElementById('btn-back-to-list')?.addEventListener('click', () => {
        document.getElementById('adjuster-detail-view')?.classList.add('hidden');
        document.getElementById('adjuster-list-view')?.classList.remove('hidden');
        currentInvestigation = null;
    });
}

function setupDetailTabs() {
    document.querySelectorAll('.detail-tab').forEach(tab => {
        tab.addEventListener('click', () => showTab(tab.getAttribute('data-tab')));
    });
}

function showTab(tabName) {
    document.querySelectorAll('.detail-tab').forEach(t => {
        t.classList.remove('text-white', 'border-brand-500');
        t.classList.add('text-slate-400', 'border-transparent');
    });
    document.querySelectorAll('.detail-tab-content').forEach(c => c.classList.add('hidden'));

    const activeTab = document.querySelector(`.detail-tab[data-tab="${tabName}"]`);
    if (activeTab) { activeTab.classList.add('text-white', 'border-brand-500'); activeTab.classList.remove('text-slate-400', 'border-transparent'); }
    document.getElementById(`tab-${tabName}`)?.classList.remove('hidden');
}

function setupVerdictButtons() {
    document.querySelectorAll('.verdict-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const verdict = btn.getAttribute('data-verdict');
            const verdictLabels = {approved:'Claim Approved', partial:'Partially Approved', denied:'Claim Denied'};
            const verdictColors = {approved:'text-emerald-400', partial:'text-amber-400', denied:'text-rose-400'};
            const container = document.getElementById('detail-verdict-content');
            const verdictIcons = {
                approved: `<svg class="w-12 h-12 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="9 12 12 15 15 9"/></svg>`,
                denied:   `<svg class="w-12 h-12 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
                partial:  `<svg class="w-12 h-12 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
            };
            container.innerHTML = `<div class="flex justify-center mb-4">${verdictIcons[verdict]}</div>
                <p class="text-2xl font-bold ${verdictColors[verdict]} mb-2">${verdictLabels[verdict]}</p>
                <p class="text-sm text-slate-400 mt-2">Verdict issued on ${new Date().toLocaleDateString()} for case ${currentInvestigation?.case_number || '—'}</p>`;
        });
    });
}

// ── PHOTOS ────────────────────────────────────────────────────────────────

async function loadPhotos(caseNumber) {
    const grid = document.getElementById('detail-photos-grid');
    if (!grid) return;
    try {
        const resp = await fetch(`/api/db/investigations/${encodeURIComponent(caseNumber)}/photos`);
        const photos = await resp.json();
        if (!photos?.length) {
            grid.innerHTML = '<div class="text-slate-500 text-sm col-span-3">No photos uploaded yet. Use the Upload button to add damage documentation.</div>';
            return;
        }
        grid.innerHTML = photos.map(p => `
            <div class="group relative rounded-xl overflow-hidden border border-white/10 hover:border-brand-500/50 transition-all cursor-pointer">
                <img src="/static/img/investigations/${p.filename}" alt="${p.caption || 'Damage photo'}"
                    class="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                    onerror="this.src='data:image/svg+xml,<svg xmlns=&quot;http://www.w3.org/2000/svg&quot; viewBox=&quot;0 0 400 300&quot;><rect fill=&quot;%231e293b&quot; width=&quot;400&quot; height=&quot;300&quot;/><text x=&quot;200&quot; y=&quot;150&quot; fill=&quot;%2364748b&quot; text-anchor=&quot;middle&quot; font-size=&quot;14&quot;>Photo not found</text></svg>'">
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div class="absolute bottom-0 left-0 right-0 p-3 transform translate-y-full group-hover:translate-y-0 transition-transform">
                    <p class="text-white text-xs font-medium">${p.caption || 'Damage photo'}</p>
                    <p class="text-slate-400 text-[10px] mt-0.5">${p.photo_type} · ${new Date(p.uploaded_at).toLocaleDateString()}</p>
                </div>
                <div class="absolute top-2 right-2 bg-black/60 rounded-full px-2 py-0.5 text-[10px] text-slate-300 uppercase">${p.photo_type}</div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = '<div class="text-rose-400 text-sm col-span-3">Failed to load photos</div>';
    }
}

function setupPhotoUpload() {
    document.getElementById('photo-upload-input')?.addEventListener('change', async (e) => {
        const files = e.target.files;
        if (!files?.length || !currentInvestigation) return;

        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('caption', `Uploaded: ${file.name}`);
            formData.append('photo_type', 'damage');
            try {
                await fetch(`/api/db/investigations/${encodeURIComponent(currentInvestigation.case_number)}/photos`, {
                    method: 'POST', body: formData
                });
            } catch (err) { console.error('Upload failed:', err); }
        }
        // Reload photos
        loadPhotos(currentInvestigation.case_number);
        e.target.value = ''; // Reset input
    });
}

// ── AI ANALYSIS ───────────────────────────────────────────────────────────

function setupAIAnalysis() {
    document.getElementById('btn-run-ai-analysis')?.addEventListener('click', runAIAnalysis);
}

async function runAIAnalysis() {
    if (!currentInvestigation) return;
    const caseNumber = currentInvestigation.case_number;
    const lang = localStorage.getItem('veritwin_lang') || 'en';
    const btn = document.getElementById('btn-run-ai-analysis');
    const fraudContainer = document.getElementById('detail-ai-fraud');
    const damageContainer = document.getElementById('detail-ai-damage');

    // Disable button during analysis
    btn.disabled = true;
    btn.innerHTML = '<div class="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div> <span>Analyzing...</span>';

    // Reset containers
    fraudContainer.innerHTML = '<p class="text-slate-300 text-sm italic animate-pulse">AI is analyzing telemetry, components, and incident data...</p>';
    damageContainer.innerHTML = '';

    try {
        const resp = await fetch(`/api/ai/investigation/${encodeURIComponent(caseNumber)}?lang=${lang}`);
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';

        // Stream into the fraud container
        fraudContainer.innerHTML = '';

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value, {stream: true});
            fullText += chunk;

            // Render markdown-ish content
            fraudContainer.innerHTML = renderMarkdown(fullText);
            fraudContainer.scrollTop = fraudContainer.scrollHeight;
        }

        // Final render with full markdown
        fraudContainer.innerHTML = renderMarkdown(fullText);
        fraudContainer.style.maxHeight = '600px';
        fraudContainer.style.overflowY = 'auto';

    } catch (err) {
        fraudContainer.innerHTML = `<p class="text-rose-400 text-sm">AI analysis failed: ${err.message}</p>`;
    }

    // Re-enable button
    btn.disabled = false;
    btn.innerHTML = '<span>Re-run AI Analysis</span>';
}

function renderMarkdown(text) {
    // Basic markdown → HTML conversion
    let html = text
        .replace(/### (.*)/g, '<h3 class="text-lg font-bold text-white mt-4 mb-2">$1</h3>')
        .replace(/## (.*)/g, '<h2 class="text-xl font-bold text-white mt-5 mb-2">$1</h2>')
        .replace(/# (.*)/g, '<h1 class="text-2xl font-bold text-white mt-6 mb-3">$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
        .replace(/^\- (.*)/gm, '<li class="text-slate-300 text-sm ml-4">$1</li>')
        .replace(/^\* (.*)/gm, '<li class="text-slate-300 text-sm ml-4">$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');

    // Wrap consecutive <li> in <ul>
    html = html.replace(/(<li.*?<\/li>(<br>)?)+/g, (match) => {
        return '<ul class="list-disc space-y-1 my-2">' + match.replace(/<br>/g, '') + '</ul>';
    });

    return `<div class="text-slate-300 text-sm leading-relaxed prose-sm">${html}</div>`;
}