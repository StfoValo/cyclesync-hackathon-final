import { componentIcon } from '/static/js/icons.js?v=18';

let cachedEsgData = null;
let cachedStats = null;
let isInitialized = false;
let currentFilter = '', currentStatus = '', currentPage = 1, totalComponents = 0;
const PER_PAGE = 15;

export function initESG() {
    loadESGDashboard();
    loadComponentStats();       // also renders dynamic chips + category cards + batch grid
    loadComponentTable();
    if (!isInitialized) {
        setupSubTabs();
        setupReverseLogistics();
        setupStatusToggle();
        setupComponentSort();
        setupPagination();
        setupBatchRecycling();
        isInitialized = true;
    }
}

// ── Sub-Tab Navigation ───────────────────────────────────────────────────
function setupSubTabs() {
    document.querySelectorAll('.esg-subtab').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.esg-subtab').forEach(b => {
                b.classList.remove('active', 'text-white', 'border-brand-500');
                b.classList.add('text-slate-400', 'border-transparent');
            });
            btn.classList.add('active', 'text-white', 'border-brand-500');
            btn.classList.remove('text-slate-400', 'border-transparent');
            document.querySelectorAll('.esg-subtab-content').forEach(c => c.classList.add('hidden'));
            const target = document.getElementById('esg-subtab-' + btn.dataset.subtab);
            if (target) target.classList.remove('hidden');
            if (btn.dataset.subtab === 'triage') renderBatchGrid(cachedStats);
        });
    });
}

// ── Batch Recycling AI ───────────────────────────────────────────────────
function setupBatchRecycling() {
    const btn = document.getElementById('btn-batch-recycling');
    if (!btn) return;
    btn.addEventListener('click', async () => {
        const category = document.getElementById('batch-category-select')?.value || 'all';
        const output = document.getElementById('batch-recycling-output');
        const dot = document.getElementById('batch-status-dot');
        const statusText = document.getElementById('batch-status-text');
        if (!output) return;

        btn.disabled = true;
        const orig = btn.innerHTML;
        btn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> Analyzing...';
        if (dot) { dot.classList.remove('bg-emerald-500'); dot.classList.add('bg-amber-500'); }
        if (statusText) statusText.textContent = window.t('esg-ai-progress', 'AI analysis in progress…');
        output.innerHTML = '<div id="batch-content"></div>';

        try {
            const lang = localStorage.getItem('veritwin_lang') || 'en';
            const res = await fetch(`/api/ai/batch-recycling/${encodeURIComponent(category)}?lang=${lang}`);
            if (!res.ok) throw new Error("HTTP " + res.status);
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            const contentDiv = document.getElementById('batch-content');
            let fullText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                fullText += decoder.decode(value, { stream: true });
                if (contentDiv) {
                    contentDiv.innerHTML = (typeof marked !== 'undefined')
                        ? marked.parse(fullText)
                        : renderMd(fullText);
                    contentDiv.classList.add('prose-ai');
                }
                output.scrollTop = output.scrollHeight;
            }
            if (dot) { dot.classList.remove('bg-amber-500'); dot.classList.add('bg-emerald-500'); }
            if (statusText) statusText.textContent = window.t('esg-ai-complete', 'Analysis complete ✓');
        } catch(e) {
            console.error(e);
            output.innerHTML = `<div class="text-rose-400 p-4">${window.t('esg-ai-failed', 'Analysis failed. Try again.')}</div>`;
            if (statusText) statusText.textContent = window.t('esg-ai-error', 'Error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = orig;
        }
    });
}

function renderMd(text) {
    let t = text.replace(/UNIPOL/gi, 'CycleSync');
    t = t.replace(/### (.*?)(?:\n|$)/g, '<h4 class="text-white font-bold text-lg border-b border-white/10 pb-2 mt-6 mb-3">$1</h4>');
    t = t.replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-400 font-semibold">$1</strong>');
    t = t.replace(/^\* (.*?)(?:\n|$)/gm, '<div class="flex items-start gap-2 mb-1.5"><span class="text-emerald-500 mt-0.5">•</span><span class="text-slate-300">$1</span></div>');
    t = t.replace(/\n/g, '<br>');
    return t;
}

// ── DB Stats KPIs + dynamic chips/cards ───────────────────────────────────
async function loadComponentStats() {
    try {
        const res = await fetch('/api/db/components/stats');
        if (!res.ok) return;
        const s = await res.json();
        cachedStats = s;
        setText('esg-kpi-total-components', s.total_components.toLocaleString());
        setText('esg-kpi-stocked', s.stocked.toLocaleString());
        setText('esg-kpi-recovery-value', '€' + s.total_recovery_value_eur.toLocaleString());
        renderCategoryGrid(s);
        renderFilterChips(s);
        renderBatchGrid(s);
        renderBatchSelectOptions(s);
    } catch(e) { console.error(e); }
}

// Tailwind color → border/text utility maps (kept narrow to avoid PurgeCSS misses).
const COLOR_CLASSES = {
    emerald: { border: 'border-emerald-500/50', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    amber:   { border: 'border-amber-500/50',   text: 'text-amber-400',   bg: 'bg-amber-500/10' },
    rose:    { border: 'border-rose-500/50',    text: 'text-rose-400',    bg: 'bg-rose-500/10' },
    blue:    { border: 'border-blue-500/50',    text: 'text-blue-400',    bg: 'bg-blue-500/10' },
    yellow:  { border: 'border-yellow-500/50',  text: 'text-yellow-400',  bg: 'bg-yellow-500/10' },
    orange:  { border: 'border-orange-500/50',  text: 'text-orange-400',  bg: 'bg-orange-500/10' },
    slate:   { border: 'border-slate-500/50',   text: 'text-slate-300',   bg: 'bg-slate-500/10' },
};
function colorOf(name) { return COLOR_CLASSES[name] || COLOR_CLASSES.slate; }

function renderCategoryGrid(s) {
    const grid = document.getElementById('esg-category-grid');
    if (!grid || !s.categories) return;
    grid.innerHTML = s.categories.map(c => {
        const col = colorOf(c.color);
        const iconSvg = componentIcon(c.key, `w-7 h-7 ${col.text}`);
        return `
            <div class="glass-panel rounded-xl p-4 border ${col.border} ${col.bg} transition-all hover:scale-[1.02]">
                <div class="flex items-center justify-between mb-2">
                    ${iconSvg}
                    <span class="text-[10px] text-slate-400 uppercase tracking-wider">${c.label}</span>
                </div>
                <p class="text-2xl md:text-3xl font-bold ${col.text}">${c.total.toLocaleString()}</p>
                <div class="text-[10px] text-slate-500 mt-1">
                    <span class="text-white font-semibold">${c.installed}</span> ${window.t('esg-installed', 'installed')} ·
                    <span class="text-white font-semibold">${c.stocked}</span> ${window.t('esg-stocked', 'stocked')}
                </div>
                <div class="text-[11px] mt-2 grid grid-cols-2 gap-1">
                    <div class="text-slate-400">€<span class="text-emerald-400 font-semibold">${c.value_eur.toLocaleString()}</span></div>
                    <div class="text-slate-400 text-right">CO₂ <span class="text-emerald-400 font-semibold">${c.co2_kg.toLocaleString()} kg</span></div>
                </div>
                <div class="text-[10px] text-slate-500 mt-1">${window.t('esg-avg-wear', 'Avg wear')} ${c.avg_wear}%</div>
            </div>`;
    }).join('');
}

function renderFilterChips(s) {
    const container = document.getElementById('component-filter-chips');
    if (!container || !s.categories) return;
    // Preserve the always-present "All Types" chip; append a chip per category.
    const existing = container.querySelector('[data-filter=""]');
    container.innerHTML = '';
    if (existing) container.appendChild(existing);
    s.categories.forEach(c => {
        const col = colorOf(c.color);
        const chip = document.createElement('button');
        chip.className = `component-filter inline-flex items-center gap-1.5 bg-slate-800 text-slate-400 text-xs font-bold px-4 py-2 rounded-full border border-white/10 hover:${col.border} transition-all`;
        chip.dataset.filter = c.key;
        chip.innerHTML = `${componentIcon(c.key, `w-3.5 h-3.5 ${col.text}`)} <span>${c.label}</span> <span class="ml-1 text-[10px] text-slate-500">${c.total}</span>`;
        container.appendChild(chip);
    });
    // (Re)wire all chips — both the persistent "All" one and the new dynamic ones.
    container.querySelectorAll('.component-filter').forEach(btn => {
        btn.addEventListener('click', () => {
            container.querySelectorAll('.component-filter').forEach(b => {
                b.classList.remove('active', 'bg-brand-600', 'text-white');
                b.classList.add('bg-slate-800', 'text-slate-400');
            });
            btn.classList.add('active', 'bg-brand-600', 'text-white');
            btn.classList.remove('bg-slate-800', 'text-slate-400');
            currentFilter = btn.dataset.filter;
            currentPage = 1;
            loadComponentTable();
        });
    });
}

function renderBatchGrid(s) {
    const grid = document.getElementById('batch-stock-grid');
    if (!grid || !s || !s.categories) return;
    const allCard = `
        <div class="glass-panel rounded-xl p-4 border border-white/5 cursor-pointer hover:border-brand-500/50 transition-all batch-category-card" data-category="all">
            <p class="text-[10px] text-slate-400 uppercase tracking-wider mb-1">All Stock</p>
            <p class="text-xl font-bold text-white">${s.stocked.toLocaleString()}</p>
            <p class="text-[10px] text-slate-500">components</p>
        </div>`;
    const catCards = s.categories
        .filter(c => c.stocked > 0)
        .map(c => {
            const col = colorOf(c.color);
            const iconSvg = componentIcon(c.key, `w-5 h-5 ${col.text}`);
            return `
                <div class="glass-panel rounded-xl p-4 border border-white/5 cursor-pointer hover:${col.border} transition-all batch-category-card" data-category="${c.key}">
                    <div class="flex items-center gap-2 mb-1">${iconSvg}<p class="text-[10px] text-slate-400 uppercase tracking-wider">${c.label}</p></div>
                    <p class="text-xl font-bold ${col.text}">${(c.stocked || 0).toLocaleString()}</p>
                    <p class="text-[10px] text-slate-500">${window.t('esg-stocked', 'stocked')} · €${(c.value_eur || 0).toLocaleString()}</p>
                </div>`;
        }).join('');
    grid.innerHTML = allCard + catCards;
    grid.querySelectorAll('.batch-category-card').forEach(card => {
        card.addEventListener('click', () => {
            const sel = document.getElementById('batch-category-select');
            if (sel) sel.value = card.dataset.category;
            grid.querySelectorAll('.batch-category-card').forEach(c => c.classList.remove('border-emerald-500/50', 'bg-emerald-500/5'));
            card.classList.add('border-emerald-500/50', 'bg-emerald-500/5');
        });
    });
}

function renderBatchSelectOptions(s) {
    const sel = document.getElementById('batch-category-select');
    if (!sel || !s.categories) return;
    // Keep the "All Stocked Components" option, add one per category.
    sel.innerHTML = '<option value="all">All Stocked Components</option>' +
        s.categories
            .filter(c => c.stocked > 0)
            .map(c => `<option value="${c.key}">${c.label} (${c.stocked})</option>`)
            .join('');
}

// ── Component Table (DB-backed) ──────────────────────────────────────────
async function loadComponentTable() {
    const tbody = document.getElementById('component-table-body');
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="9" class="px-4 py-8 text-center text-slate-500">${window.t('reg-loading', 'Loading…')}</td></tr>`;
    try {
        let url = `/api/db/components?page=${currentPage}&per_page=${PER_PAGE}`;
        if (currentFilter) url += `&category=${encodeURIComponent(currentFilter)}`;
        if (currentStatus) url += `&status=${encodeURIComponent(currentStatus)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("HTTP " + res.status);
        const data = await res.json();
        totalComponents = data.total;
        renderTable(data.components);
        updatePagination(data);
        updateFooter(data);
    } catch(e) {
        console.error(e);
        if (tbody) tbody.innerHTML = '<tr><td colspan="9" class="px-4 py-8 text-center text-rose-400">Failed to load</td></tr>';
    }
}

// Human-friendly label for any category key (falls back to slug-title-case).
function categoryLabel(key) {
    const c = cachedStats?.categories?.find(c => c.key === key);
    return c?.label || (key || '').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}
function categoryIconStr(key) {
    // Return a stylized SVG that matches the driver-app icons.
    return componentIcon(key, 'w-4 h-4 text-slate-300');
}

function renderTable(comps) {
    const tbody = document.getElementById('component-table-body');
    if (!tbody || !comps.length) { if(tbody) tbody.innerHTML = `<tr><td colspan="9" class="px-4 py-8 text-center text-slate-500">${window.t('esg-no-components-table', 'No components')}</td></tr>`; return; }
    tbody.innerHTML = comps.map((c,i) => {
        const rec = c.ai_recommendation || '—';
        const isReuse = /Retread|Resell|Second-Life|Grid Storage|Reuse/i.test(rec);
        const isRecycle = /Recycle|Recovery|Smelting|Black Mass|Refining|Lead-Acid|Asphalt|Friction/i.test(rec);
        const rowB = c.status==='installed' ? 'border-l-2 border-l-brand-500' : isReuse ? 'border-l-2 border-l-emerald-500' : isRecycle ? 'border-l-2 border-l-amber-500' : 'border-l-2 border-l-slate-600';
        const recC = isReuse ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' : isRecycle ? 'text-amber-400 bg-amber-500/10 border-amber-500/30' : 'text-slate-400 bg-slate-500/10 border-slate-500/30';
        const w = c.wear_percent||0;
        const wC = w>=80?'bg-rose-500':w>=60?'bg-amber-500':'bg-emerald-500';
        const wT = w>=80?'text-rose-400':w>=60?'text-amber-400':'text-emerald-400';
        const hC = {healthy:'text-emerald-400 bg-emerald-500/10',warning:'text-amber-400 bg-amber-500/10',critical:'text-rose-400 bg-rose-500/10',end_of_life:'text-slate-300 bg-slate-500/10'}[c.health_status]||'text-slate-400 bg-slate-500/10';
        // Build a per-category specs hint.
        let hint='';
        if(c.specs){
            if(c.category==='tire' && c.specs.tread_depth_mm) hint=`${c.specs.tread_depth_mm}mm tread`;
            else if(c.category==='ev_battery' && c.specs.capacity_kwh) hint=`${c.specs.capacity_kwh}kWh · SOH ${c.specs.soh_percent}%`;
            else if(c.category==='brake_pad') hint=`${c.specs.thickness_mm}mm`;
            else if(c.category==='brake_disc') hint=`${c.specs.thickness_mm}mm`;
            else if(c.category==='aux_12v_battery') hint=`${c.specs.capacity_ah}Ah ${c.specs.chemistry||''}`;
            else if(c.category==='engine_oil') hint=`${c.specs.viscosity} · ${c.specs.volume_l}L`;
            else if(c.category==='dpf') hint=`Soot ${c.specs.soot_loaded_g}g`;
            else if(c.category==='suspension_damper') hint=`${c.specs.type||''}`;
        }
        const catLabel = categoryLabel(c.category);
        const catIcon = categoryIconStr(c.category);
        return `<tr class="${rowB} hover:bg-white/[0.02] cursor-pointer transition-colors component-row" data-index="${i}">
            <td class="px-4 py-3 font-mono text-xs text-slate-300">${c.serial_number||'—'}</td>
            <td class="px-4 py-3"><span class="flex items-center gap-1.5"><span>${catIcon}</span><span class="text-white text-xs">${catLabel}</span></span>${c.position?`<span class="text-[10px] text-slate-500 block mt-0.5">${c.position}</span>`:''}</td>
            <td class="px-4 py-3"><span class="text-white text-xs">${c.brand||'—'}</span><span class="text-[10px] text-slate-500 block mt-0.5">${c.model_name||'—'}${hint?' · '+hint:''}</span></td>
            <td class="px-4 py-3"><div class="flex items-center gap-2"><div class="w-16 bg-slate-700 rounded-full h-1.5"><div class="${wC} rounded-full h-1.5" style="width:${w}%"></div></div><span class="text-xs font-bold ${wT}">${w}%</span></div></td>
            <td class="px-4 py-3"><span class="font-mono font-bold text-white text-xs bg-black/40 px-1.5 py-0.5 rounded border border-slate-700">${c.plate_number||'—'}</span></td>
            <td class="px-4 py-3"><span class="text-[10px] font-bold px-2 py-1 rounded-full ${hC}">${c.status}</span></td>
            <td class="px-4 py-3">${rec!=='—'?`<span class="text-[10px] font-bold px-2 py-1 rounded-full border ${recC}">${rec}</span>`:'<span class="text-slate-600 text-xs">—</span>'}</td>
            <td class="px-4 py-3 text-xs font-bold ${c.recovery_value_eur?'text-emerald-400':'text-slate-600'}">${c.recovery_value_eur?'€'+c.recovery_value_eur.toLocaleString():'—'}</td>
            <td class="px-4 py-3 text-xs font-bold ${c.co2_saved_kg?'text-emerald-400':'text-slate-600'}">${c.co2_saved_kg?c.co2_saved_kg+' kg':'—'}</td>
        </tr>
        <tr class="component-detail hidden bg-black/20" data-detail-index="${i}"><td colspan="9" class="px-6 py-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div><p class="text-slate-400 font-semibold uppercase tracking-wider mb-1">${window.t('esg-ai-reasoning','AI Reasoning')}</p><p class="text-slate-300">${c.ai_reasoning||window.t('esg-no-ai-analysis','No AI analysis available.')}</p></div>
                <div><p class="text-slate-400 font-semibold uppercase tracking-wider mb-1">${window.t('esg-lifecycle','Lifecycle')}</p><p class="text-slate-300">${window.t('esg-installed-on','Installed:')} ${c.installed_date||'—'} ${c.installed_km?`${window.t('esg-at','at')} ${c.installed_km.toLocaleString()} km`:''}</p>${c.removed_date?`<p class="text-slate-300">${window.t('esg-removed-on','Removed:')} ${c.removed_date}${c.removed_km?` ${window.t('esg-at','at')} ${c.removed_km.toLocaleString()} km`:''}</p>`:''}${c.removal_reason?`<p class="text-slate-400 mt-1">${window.t('esg-reason','Reason:')} <span class="text-slate-200">${c.removal_reason}</span></p>`:''}${c.destination_facility?`<p class="text-slate-300 mt-1">${window.t('esg-facility','Facility:')} <span class="text-brand-400">${c.destination_facility}</span></p>`:''}</div>
                <div><p class="text-slate-400 font-semibold uppercase tracking-wider mb-1">${window.t('esg-specs','Specs')}</p>${c.specs?Object.entries(c.specs).map(([k,v])=>`<p class="text-slate-300">${k.replace(/_/g,' ')}: <span class="text-white font-medium">${v}</span></p>`).join(''):'<p class="text-slate-500">—</p>'}</div>
            </div>
        </td></tr>`;
    }).join('');
    tbody.querySelectorAll('.component-row').forEach(r => r.addEventListener('click', () => {
        const d = tbody.querySelector(`[data-detail-index="${r.dataset.index}"]`);
        if(d) d.classList.toggle('hidden');
    }));
}

function updateFooter(d) {
    setText('comp-showing', `${(d.page-1)*d.per_page+1}–${Math.min(d.page*d.per_page, d.total)}`);
    setText('comp-total-count', d.total);
    if (cachedStats) {
        setText('comp-total-value', '€'+cachedStats.total_recovery_value_eur.toLocaleString());
        setText('comp-total-co2', cachedStats.total_co2_saved_kg.toLocaleString()+' kg');
    }
}

function updatePagination(d) {
    const tp = Math.ceil(d.total/d.per_page);
    const prev = document.getElementById('comp-prev-page'), next = document.getElementById('comp-next-page');
    setText('comp-page-info', `Page ${d.page} of ${tp}`);
    if(prev) prev.disabled = d.page<=1;
    if(next) next.disabled = d.page>=tp;
}

function setupPagination() {
    document.getElementById('comp-prev-page')?.addEventListener('click', () => { if(currentPage>1){currentPage--;loadComponentTable();} });
    document.getElementById('comp-next-page')?.addEventListener('click', () => { currentPage++; loadComponentTable(); });
}

function setupStatusToggle() {
    document.querySelectorAll('.esg-status-toggle').forEach(btn => btn.addEventListener('click', () => {
        document.querySelectorAll('.esg-status-toggle').forEach(b => { b.classList.remove('bg-brand-600','text-white'); b.classList.add('text-slate-400'); });
        btn.classList.add('bg-brand-600','text-white'); btn.classList.remove('text-slate-400');
        currentStatus = btn.dataset.status; currentPage = 1; loadComponentTable();
    }));
}

function setupComponentSort() {
    document.querySelectorAll('th[data-sort]').forEach(th => { let asc=true; th.addEventListener('click', () => { asc=!asc; }); });
}

function setText(id, val) { const el = document.getElementById(id); if(el) el.textContent = val; }
const getT = (key) => window.translations?.[localStorage.getItem('veritwin_lang')||'en']?.[key] || key;

// ── Reverse Logistics (AI Streaming) ─────────────────────────────────────
function setupReverseLogistics() {
    const btn = document.getElementById('btn-generate-manifest');
    const terminal = document.getElementById('logistics-terminal');
    const regionSelect = document.getElementById('logistics-region');
    if (!btn || !terminal || !regionSelect) return;
    btn.addEventListener('click', () => {
        const region = regionSelect.value;
        btn.disabled = true; const orig = btn.innerHTML; btn.innerHTML = getT('term-run')+'...';
        terminal.innerHTML = '';
        const spin = `<svg class="w-4 h-4 text-brand-500 animate-spin inline-block mr-2" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>`;
        const chk = `<svg class="w-4 h-4 text-emerald-400 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
        setTimeout(()=>{terminal.innerHTML+=`<div id="step1" class="text-slate-300 mb-2">${spin} Ingesting OEM Blueprints...</div>`;},0);
        setTimeout(()=>{document.getElementById('step1').innerHTML=`${chk} OEM Blueprints Ingested.`;terminal.innerHTML+=`<div id="step2" class="text-slate-300 mb-2">${spin} Analyzing VSI degradation...</div>`;},600);
        setTimeout(()=>{document.getElementById('step2').innerHTML=`${chk} Degradation Analyzed.`;terminal.innerHTML+=`<div id="step3" class="text-slate-300 mb-4">${spin} Cross-referencing recycling network...</div>`;},1200);
        setTimeout(async()=>{
            try{
                const lang=localStorage.getItem('veritwin_lang')||'en';
                const res=await fetch(`/api/ai/circular-logistics/${encodeURIComponent(region)}?lang=${lang}`);
                if(!res.ok)throw new Error("HTTP "+res.status);
                const reader=res.body.getReader();const decoder=new TextDecoder();
                terminal.innerHTML='<div id="manifest-content"></div>';const cd=document.getElementById('manifest-content');cd.classList.add('prose-ai');let ft="";
                while(true){const{done,value}=await reader.read();if(done)break;ft+=decoder.decode(value,{stream:true});if(cd)cd.innerHTML=(typeof marked!=='undefined')?marked.parse(ft):renderMd(ft);terminal.scrollTop=terminal.scrollHeight;}
            }catch(e){console.error(e);terminal.innerHTML='<div class="text-red-400 p-4 bg-red-400/10 rounded-lg border border-red-400/20">System Timeout</div>';}
            finally{btn.disabled=false;btn.innerHTML=orig;}
        },1800);
    });
}

// ── ESG Dashboard (emissions KPIs only — circular data now from /stats) ───
async function loadESGDashboard() {
    try {
        if(cachedEsgData){renderESG(cachedEsgData);return;}
        const _loading = window.t('reg-loading', 'Loading…');
        setText('esg-kpi-baseline', _loading); setText('esg-kpi-real', _loading); setText('esg-kpi-saved', _loading);
        const res = await fetch('/api/actuarial/esg');
        if(!res.ok)throw new Error("HTTP "+res.status);
        cachedEsgData = await res.json();
        renderESG(cachedEsgData);
    }catch(e){console.error(e);setText('esg-kpi-baseline','Error');}
}

function renderESG(data) {
    const em = data.emissions;
    if (!em) return;
    setText('esg-kpi-baseline', em.baseline_co2_tons.toLocaleString(undefined,{maximumFractionDigits:0}));
    setText('esg-kpi-real',     em.real_telematics_co2_tons.toLocaleString(undefined,{maximumFractionDigits:0}));
    setText('esg-kpi-saved',    em.co2_saved_tons.toLocaleString(undefined,{maximumFractionDigits:0}));
}


// Re-render dynamic ESG content (category cards, filter chips, batch grid,
// inventory table) when the language toggles so labels follow the new locale.
window.addEventListener('languageChanged', () => {
    if (cachedStats) {
        renderCategoryGrid(cachedStats);
        renderFilterChips(cachedStats);
        renderBatchGrid(cachedStats);
        renderBatchSelectOptions(cachedStats);
    }
    loadComponentTable();
});
