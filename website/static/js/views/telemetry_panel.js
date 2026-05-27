/**
 * Shared "categorized live telemetry" renderer.
 *
 * Used by:
 *   • Vehicle Passport  (Fleet Telemetry → Live Telemetry & Sensors)
 *   • Adjuster Detail   (Telemetry tab)
 *
 * Two sub-tabs at the top:
 *   • Essential — curated subset per category (the at-a-glance dashboard view)
 *   • Extended  — every raw signal carried by vehicle_telemetry (all 18 cats)
 *
 * The catalogue is fetched once from GET /api/db/telemetry/categories and
 * cached for the page lifetime; values that aren't populated yet render as
 * "—" so the layout shows the *structure* even before data generation.
 */

let _categoriesPromise = null;

export function loadTelemetryCategories() {
    if (!_categoriesPromise) {
        _categoriesPromise = fetch('/api/db/telemetry/categories?v=1')
            .then(r => r.json())
            .then(d => d.categories || [])
            .catch(() => []);
    }
    return _categoriesPromise;
}

// Translation key per telemetry category (used by renderCategorizedTelemetry).
const CATEGORY_I18N = {
    gps:             'tel-cat-gps',
    imu:             'tel-cat-imu',
    crash_event:     'tel-cat-crash',
    obd_engine:      'tel-cat-engine',
    obd_fuel:        'tel-cat-fuel',
    speed:           'tel-cat-speed',
    emissions:       'tel-cat-emissions',
    electrical_12v:  'tel-cat-12v',
    brake:           'tel-cat-brake',
    steering:        'tel-cat-steering',
    transmission:    'tel-cat-transmission',
    tpms:            'tel-cat-tpms',
    ev_hybrid:       'tel-cat-evhybrid',
    adas:            'tel-cat-adas',
    behavior:        'tel-cat-behavior',
    dtc:             'tel-cat-dtc',
    trip:            'tel-cat-trip',
    device:          'tel-cat-device',
};

// Translation keys for the columns we surface in Essential mode. Anything
// not in this map falls back to the auto-prettified label from prettifyTelCol.
const COL_I18N = {
    accel_x_g:                'tel-col-accel-x',
    gyro_roll_deg_s:          'tel-col-gyro-roll',
    abs_active:               'tel-col-abs-active',
    esc_active:               'tel-col-esc-active',
    engine_rpm:               'tel-col-engine-rpm',
    coolant_temp_c:           'tel-col-coolant-temp',
    throttle_position_pct:    'tel-col-throttle',
    fuel_level_pct:           'tel-col-fuel-level',
    brake_pressure_bar:       'tel-col-brake-pressure',
    transmission_fluid_temp_c:'tel-col-trans-fluid-temp',
    tpms_fl_bar:              'tel-col-tpms-fl',
    tpms_fr_bar:              'tel-col-tpms-fr',
    tpms_rl_bar:              'tel-col-tpms-rl',
    tpms_rr_bar:              'tel-col-tpms-rr',
    motor_speed_rpm:          'tel-col-motor-rpm',
    motor_temp_c:             'tel-col-motor-temp',
    inverter_temp_c:          'tel-col-inverter-temp',
    battery_pack_voltage_v:   'tel-col-battery-voltage',
    battery_energy_kwh:       'tel-col-battery-energy',
    estimated_range_km:       'tel-col-range',
};

const _t = (key, fallback) => (window.t ? window.t(key, fallback) : fallback);

// ── Curated "Essential" subset per category ──────────────────────────────
// '*'        → all columns of the category
// []         → category hidden in Essential view
// ['__map__']→ render the GPS mini-map placeholder instead of cards
// [col,…]    → only those columns
const ESSENTIAL_FIELDS = {
    gps:           ['__map__'],
    imu:           ['accel_x_g', 'gyro_roll_deg_s'],          // forward accel + roll rate
    crash_event:   ['abs_active', 'esc_active'],
    obd_engine:    ['engine_rpm', 'coolant_temp_c', 'throttle_position_pct'],
    obd_fuel:      ['fuel_level_pct'],
    speed:         [],
    emissions:     [],
    electrical_12v:[],
    brake:         ['brake_pressure_bar'],
    steering:      [],
    transmission:  ['transmission_fluid_temp_c'],
    tpms:          ['tpms_fl_bar', 'tpms_fr_bar', 'tpms_rl_bar', 'tpms_rr_bar'],
    ev_hybrid:     ['motor_speed_rpm', 'motor_temp_c', 'inverter_temp_c',
                    'battery_pack_voltage_v', 'battery_energy_kwh', 'estimated_range_km'],
    adas:          '*',
    behavior:      '*',
    dtc:           [],
    trip:          [],
    device:        [],
};

// Every column on `vehicle_telemetry` is now realistically gettable from
// the OBD-II port and/or a UNIPOL-style insurance blackbox. Non-feasible
// columns (brake disc temp, alternator current, airbag-deployed flag) have
// been removed from the schema by the telemetry_seeder DROP-COLUMN step.
const QUESTIONABLE_COLS = new Set();

// ── Column-name prettifier ───────────────────────────────────────────────
const UNIT_SUFFIXES = [
    ['_g_per_s', 'g/s'], ['_deg_s', '°/s'],
    ['_kmh', 'km/h'], ['_kwh', 'kWh'], ['_kpa', 'kPa'],
    ['_kw',  'kW'],   ['_pct', '%'],   ['_bar', 'bar'],
    ['_deg', '°'],    ['_dbm', 'dBm'], ['_ppm', 'ppm'],
    ['_nm',  'Nm'],   ['_pa',  'Pa'],  ['_km',  'km'],
    ['_c',   '°C'],   ['_v',   'V'],   ['_a',   'A'],
    ['_g',   'g'],    ['_m',   'm'],   ['_s',   's'],
    ['_json', ''],
];

const ACRONYMS = new Set([
    'gps','tpms','rpm','abs','esc','aeb','ldw','fcw','dtc','mil','soc','soh',
    'afr','egr','evap','nox','maf','map','o2','b1s1','b1s2','gsm','adas',
    'ev','ac','dc','hv','fl','fr','rl','rr','ecm','atf',
]);

export function prettifyTelCol(col) {
    let base = col;
    let unit = '';
    for (const [suf, u] of UNIT_SUFFIXES) {
        if (col.endsWith(suf) && col.length > suf.length) {
            base = col.slice(0, -suf.length);
            unit = u;
            break;
        }
    }
    const label = base.split('_')
        .map(p => ACRONYMS.has(p) ? p.toUpperCase() : p.charAt(0).toUpperCase() + p.slice(1))
        .join(' ');
    return { label, unit };
}

export function formatTelValue(value, unit) {
    if (value === null || value === undefined || value === '') return '—';
    if (typeof value === 'number') {
        const abs = Math.abs(value);
        const formatted = abs >= 100 ? Math.round(value).toLocaleString()
                        : abs >= 10  ? value.toFixed(1)
                        : abs >= 1   ? value.toFixed(2)
                        :              value.toFixed(3);
        return unit ? `${formatted} ${unit}` : formatted;
    }
    if (typeof value === 'string' && value.length > 80) {
        return value.slice(0, 77) + '…';
    }
    return unit ? `${value} ${unit}` : `${value}`;
}

// ── Tiny GPS mini-map ────────────────────────────────────────────────────
function _gpsMiniMap(telemetry) {
    const lat = telemetry?.gps_lat;
    const lon = telemetry?.gps_lon;
    const valid = typeof lat === 'number' && typeof lon === 'number' && !isNaN(lat) && !isNaN(lon);
    if (!valid) {
        return `<div class="col-span-2 sm:col-span-3 lg:col-span-4 bg-slate-800/50 rounded-lg p-6 border border-white/5 text-center">
            <p class="text-[11px] text-slate-400 mb-1">📡 ${_t('tel-no-gps', 'No GPS fix yet')}</p>
            <p class="text-[10px] text-slate-500">${_t('tel-no-gps-sub', 'Position will appear here once the blackbox reports lat/lon.')}</p>
        </div>`;
    }
    const d = 0.008;
    const bbox = `${lon - d},${lat - d},${lon + d},${lat + d}`;
    const marker = `${lat},${lon}`;
    const sats = telemetry?.gps_satellites ?? '—';
    const fix  = telemetry?.gps_fix_quality ?? '—';
    return `<div class="col-span-2 sm:col-span-3 lg:col-span-4 bg-slate-800/50 rounded-lg overflow-hidden border border-white/5">
        <iframe src="https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${marker}"
                class="w-full h-48 block" style="border:0" loading="lazy"></iframe>
        <div class="px-3 py-2 flex justify-between items-center bg-slate-900/50">
            <span class="text-[10px] font-mono text-slate-300">${lat.toFixed(5)}, ${lon.toFixed(5)}</span>
            <span class="text-[10px] text-slate-500">${_t('tel-sat', 'Sat')}: ${sats} · ${_t('tel-fix', 'Fix')}: ${fix}</span>
        </div>
    </div>`;
}

// ── Card + section HTML builders ─────────────────────────────────────────
function _telCard(label, value, questionable = false) {
    const dot = questionable
        ? `<span class="ml-1 text-amber-400" title="Not realistically available from standard OBD-II — see notes">⚠</span>`
        : '';
    return `
        <div class="bg-slate-800/50 rounded-lg p-2.5 border border-white/5">
            <p class="text-[10px] text-slate-400 mb-0.5 truncate" title="${label}">${label}${dot}</p>
            <p class="text-white font-medium text-xs">${value}</p>
        </div>`;
}

function _categoryLabel(category) {
    const key = CATEGORY_I18N[category.key];
    return key ? _t(key, category.label) : category.label;
}

function _colLabel(col) {
    const key = COL_I18N[col];
    const pretty = prettifyTelCol(col);
    if (key) {
        const translated = _t(key, pretty.label);
        return { label: translated, unit: pretty.unit };
    }
    return pretty;
}

function _telSection(category, telemetry, mode = 'extended') {
    const filter = mode === 'essential' ? (ESSENTIAL_FIELDS[category.key] ?? []) : '*';

    // Hide whole category in Essential mode if filter is an empty array.
    if (mode === 'essential' && Array.isArray(filter) && filter.length === 0) return '';

    const catLabel = _categoryLabel(category);

    // Special-case: GPS mini-map.
    if (mode === 'essential' && filter[0] === '__map__') {
        return `
            <div class="col-span-2 sm:col-span-4 mt-3 first:mt-0">
                <div class="flex items-center gap-2 mb-2 pb-1.5 border-b border-white/5">
                    <span class="text-sm">${category.icon}</span>
                    <h5 class="text-[11px] uppercase tracking-wider text-slate-300 font-bold">${catLabel}</h5>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                    ${_gpsMiniMap(telemetry)}
                </div>
            </div>`;
    }

    // Decide which columns to show.
    let cols;
    if (filter === '*') {
        cols = category.columns;
    } else {
        cols = category.columns.filter(c => filter.includes(c));
    }
    if (!cols.length) return '';

    const cards = cols.map(col => {
        const { label, unit } = _colLabel(col);
        const value = formatTelValue(telemetry?.[col], unit);
        return _telCard(label, value, QUESTIONABLE_COLS.has(col));
    }).join('');

    const signalsLabel = _t('tel-signals', 'signals');
    return `
        <div class="col-span-2 sm:col-span-4 mt-3 first:mt-0">
            <div class="flex items-center gap-2 mb-2 pb-1.5 border-b border-white/5">
                <span class="text-sm">${category.icon}</span>
                <h5 class="text-[11px] uppercase tracking-wider text-slate-300 font-bold">${catLabel}</h5>
                <span class="text-[10px] text-slate-600 ml-auto">${cols.length}${mode === 'essential' && filter !== '*' ? ` / ${category.columns.length}` : ''} ${signalsLabel}</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                ${cards}
            </div>
        </div>`;
}

function _buildSections(cats, telemetry, mode) {
    return cats.map(c => _telSection(c, telemetry, mode)).join('');
}

// Count how many signals are surfaced in each mode (for tab badges).
function _signalCount(cats, mode) {
    if (mode === 'extended') return cats.reduce((n, c) => n + c.columns.length, 0);
    let n = 0;
    for (const c of cats) {
        const f = ESSENTIAL_FIELDS[c.key] ?? [];
        if (f === '*') n += c.columns.length;
        else if (Array.isArray(f) && f.length && f[0] !== '__map__') {
            n += c.columns.filter(col => f.includes(col)).length;
        }
    }
    return n;
}

/**
 * Replace the contents of `gridEl` with a tabbed Essential / Extended panel.
 *
 * @param {HTMLElement} gridEl       The grid container inside the accordion.
 * @param {object}      telemetry    The live telemetry row from vehicle_telemetry.
 * @param {object}      [opts]
 * @param {string}      [opts.overviewHtml]   Optional HTML above the tab bar.
 */
// Stash last-rendered context so we can re-render on languageChanged.
const _lastRender = new WeakMap();

export async function renderCategorizedTelemetry(gridEl, telemetry, opts = {}) {
    if (!gridEl) return;
    _lastRender.set(gridEl, { telemetry, opts });
    if (!telemetry || !telemetry.vin) {
        gridEl.innerHTML = `<div class="text-slate-500 text-sm col-span-2 sm:col-span-4">${_t('tel-no-data', 'No telemetry data')}</div>`;
        return;
    }
    const cats = await loadTelemetryCategories();
    const essentialHtml = _buildSections(cats, telemetry, 'essential');
    const extendedHtml  = _buildSections(cats, telemetry, 'extended');
    const essentialN = _signalCount(cats, 'essential');
    const extendedN  = _signalCount(cats, 'extended');

    gridEl.innerHTML = `
        ${opts.overviewHtml || ''}
        <div class="col-span-2 sm:col-span-4">
            <div class="flex items-center gap-1 mb-3 border-b border-white/5">
                <button data-tel-tab="essential"
                    class="tel-subtab px-4 py-1.5 text-xs font-bold text-brand-400 border-b-2 border-brand-500 transition-colors">
                    ${_t('tel-essential', 'Essential')} <span class="opacity-60">· ${essentialN}</span>
                </button>
                <button data-tel-tab="extended"
                    class="tel-subtab px-4 py-1.5 text-xs font-bold text-slate-500 border-b-2 border-transparent hover:text-white transition-colors">
                    ${_t('tel-extended', 'Extended')} <span class="opacity-60">· ${extendedN}</span>
                </button>
            </div>
            <div data-tel-pane="essential" class="grid grid-cols-2 sm:grid-cols-4 gap-2">${essentialHtml}</div>
            <div data-tel-pane="extended"  class="grid grid-cols-2 sm:grid-cols-4 gap-2 hidden">${extendedHtml}</div>
        </div>`;

    // Wire the sub-tab toggle.
    gridEl.querySelectorAll('.tel-subtab').forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tel-tab');
            gridEl.querySelectorAll('.tel-subtab').forEach(b => {
                const active = b.getAttribute('data-tel-tab') === target;
                b.classList.toggle('text-brand-400', active);
                b.classList.toggle('border-brand-500', active);
                b.classList.toggle('text-slate-500', !active);
                b.classList.toggle('border-transparent', !active);
            });
            gridEl.querySelectorAll('[data-tel-pane]').forEach(p => {
                p.classList.toggle('hidden', p.getAttribute('data-tel-pane') !== target);
            });
        });
    });
}

// ── Re-render on language change ─────────────────────────────────────────
// Each grid element we've rendered into is tracked in _lastRender; when the
// user toggles EN ⇄ IT we re-call renderCategorizedTelemetry with the same
// telemetry + opts so section headers, field labels, "Essential/Extended",
// and the GPS footer flip to the new locale.
window.addEventListener('languageChanged', () => {
    // WeakMap doesn't expose keys; we re-render anything still attached by
    // looking up the well-known mount points used by Vehicle Passport and
    // Adjuster — those are the only callers.
    ['passport-telemetry-grid', 'adj-tel-outer'].forEach(id => {
        const el = document.getElementById(id);
        const ctx = el && _lastRender.get(el);
        if (el && ctx) renderCategorizedTelemetry(el, ctx.telemetry, ctx.opts);
    });
});
