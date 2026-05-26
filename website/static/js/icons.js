/**
 * CycleSync Icon Library
 * Custom SVG icons not available in Lucide.
 * All functions return raw SVG/HTML strings.
 */

// ─── Powertrain / Engine ────────────────────────────────────────────────────

/** Electric zap bolt */
export const iconElectric = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`;

/** Petrol fuel pump */
export const iconPetrol = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 22V6a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v16"/><path d="M14 9h2a2 2 0 0 1 2 2v2.5a1.5 1.5 0 0 0 3 0V7l-3-3"/><path d="M3 22h11"/><rect x="5" y="9" width="6" height="4" rx="1"/></svg>`;

/** Hybrid leaf + bolt */
export const iconHybrid = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>`;

/** EV Battery (more refined than lucide battery) */
export const iconBattery = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="16" height="10" rx="2"/><path d="M22 11v2"/><path d="M6 11h4M10 9v6"/></svg>`;

// ─── Auxiliary 12 V Battery ─────────────────────────────────────────────────
// Stacked-cell automotive battery with two top terminals (+ / −) and a vent
// cap row, distinguishing it from the simpler "iconBattery" line drawing.
export const iconAuxBattery = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <!-- Outer body -->
      <rect x="3" y="7" width="18" height="13" rx="1.2"/>
      <!-- Lid / top trim -->
      <line x1="3" y1="10" x2="21" y2="10"/>
      <!-- Positive terminal -->
      <rect x="5.5" y="4.5" width="3" height="2.5" rx="0.4"/>
      <line x1="6" y1="3" x2="8" y2="3"/>
      <line x1="7" y1="2" x2="7" y2="4"/>
      <!-- Negative terminal -->
      <rect x="15.5" y="4.5" width="3" height="2.5" rx="0.4"/>
      <line x1="16" y1="3" x2="18" y2="3"/>
      <!-- Vent caps (4) -->
      <circle cx="7.5"  cy="13" r="0.6"/>
      <circle cx="11"   cy="13" r="0.6"/>
      <circle cx="14"   cy="13" r="0.6"/>
      <circle cx="17"   cy="13" r="0.6"/>
      <!-- Capacity bars / cell separators -->
      <line x1="7"  y1="16" x2="9"  y2="16"/>
      <line x1="11" y1="16" x2="13" y2="16"/>
      <line x1="15" y1="16" x2="17" y2="16"/>
    </svg>`;

// ─── Suspension Damper / Strut ──────────────────────────────────────────────
// Vertical strut: top mount, coil spring around shaft, damper cylinder at base.
export const iconSuspensionDamper = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <!-- Top mounting hat -->
      <rect x="7" y="2" width="10" height="2.2" rx="0.5"/>
      <line x1="9"  y1="4.3" x2="9"  y2="5.5"/>
      <line x1="15" y1="4.3" x2="15" y2="5.5"/>
      <!-- Piston shaft -->
      <line x1="12" y1="5.5" x2="12" y2="9.5"/>
      <!-- Coil spring (zig-zag through middle) -->
      <path d="M8 7 L16 8.5 L8 10 L16 11.5 L8 13 L16 14.5"/>
      <!-- Damper cylinder body -->
      <rect x="9.5" y="15" width="5" height="6.5" rx="0.6"/>
      <!-- Mounting eye at bottom -->
      <circle cx="12" cy="21.8" r="0.9"/>
    </svg>`;

// ─── Engine Oil Bottle ──────────────────────────────────────────────────────
// Oil-can shape with a droplet inside + viscosity label tab on the side.
export const iconEngineOil = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <!-- Cap -->
      <rect x="10" y="2.5" width="4" height="2.5" rx="0.4"/>
      <!-- Neck -->
      <path d="M10 5 L9 7 L15 7 L14 5"/>
      <!-- Bottle body -->
      <path d="M9 7 L7 9 Q6 10 6 11.5 L6 19.5 Q6 21 7.5 21 L16.5 21 Q18 21 18 19.5 L18 11.5 Q18 10 17 9 L15 7 Z"/>
      <!-- Label / window -->
      <rect x="8.5" y="12" width="7" height="4.5" rx="0.5" opacity="0.55"/>
      <!-- Oil droplet inside label -->
      <path d="M12 13.2 Q10.6 14.6 10.6 15.5 A 1.4 1.4 0 0 0 13.4 15.5 Q13.4 14.6 12 13.2 Z" fill="currentColor" opacity="0.65" stroke="none"/>
    </svg>`;

// ─── Diesel Particulate Filter (DPF) ────────────────────────────────────────
// Cylindrical exhaust canister with internal honeycomb-substrate detail and
// inlet/outlet flanges + soot-flow arrow.
export const iconDpf = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
      <!-- Inlet pipe -->
      <line x1="1.5" y1="12" x2="4.5" y2="12"/>
      <!-- Left flange -->
      <line x1="4.5" y1="9" x2="4.5" y2="15"/>
      <!-- Canister body -->
      <rect x="4.5" y="7.5" width="15" height="9" rx="1.4"/>
      <!-- Right flange -->
      <line x1="19.5" y1="9" x2="19.5" y2="15"/>
      <!-- Outlet pipe -->
      <line x1="19.5" y1="12" x2="22.5" y2="12"/>
      <!-- Honeycomb substrate -->
      <line x1="7"  y1="9" x2="7"  y2="15"/>
      <line x1="9"  y1="9" x2="9"  y2="15"/>
      <line x1="11" y1="9" x2="11" y2="15"/>
      <line x1="13" y1="9" x2="13" y2="15"/>
      <line x1="15" y1="9" x2="15" y2="15"/>
      <line x1="17" y1="9" x2="17" y2="15"/>
      <line x1="5.5" y1="12" x2="18.5" y2="12" opacity="0.45"/>
    </svg>`;

// ─── Braking System ─────────────────────────────────────────────────────────

/**
 * Brake disc + caliper assembly.
 * Drilled rotor with 5-lug hub bolt pattern + ribbed caliper straddling the disc edge.
 */
export const iconBrakeDisc = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
      <!-- Rotor outer edge -->
      <circle cx="10" cy="12" r="9"/>
      <!-- Inner friction-ring edge -->
      <circle cx="10" cy="12" r="6.5" opacity="0.55"/>
      <!-- Central hub -->
      <circle cx="10" cy="12" r="2.5"/>
      <circle cx="10" cy="12" r="0.55" fill="currentColor" stroke="none"/>
      <!-- 5-lug bolt circle around hub -->
      <circle cx="10" cy="9.7" r="0.42" fill="currentColor" stroke="none"/>
      <circle cx="12.2" cy="11.3" r="0.42" fill="currentColor" stroke="none"/>
      <circle cx="11.3" cy="14" r="0.42" fill="currentColor" stroke="none"/>
      <circle cx="8.7" cy="14" r="0.42" fill="currentColor" stroke="none"/>
      <circle cx="7.8" cy="11.3" r="0.42" fill="currentColor" stroke="none"/>
      <!-- Drilled holes scattered across rotor face -->
      <circle cx="5"   cy="8.5" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/>
      <circle cx="14"  cy="6"   r="0.32" fill="currentColor" stroke="none" opacity="0.65"/>
      <circle cx="6"   cy="15.5" r="0.32" fill="currentColor" stroke="none" opacity="0.65"/>
      <circle cx="14"  cy="18"  r="0.32" fill="currentColor" stroke="none" opacity="0.65"/>
      <circle cx="3.5" cy="12"  r="0.32" fill="currentColor" stroke="none" opacity="0.65"/>
      <circle cx="16"  cy="12"  r="0.32" fill="currentColor" stroke="none" opacity="0.65"/>
      <!-- Caliper body straddling right edge of disc -->
      <path d="M14 7 L21.5 7 Q22.5 7 22.5 8 L22.5 16 Q22.5 17 21.5 17 L14 17 Z"/>
      <!-- Ribbed caliper fins -->
      <line x1="16" y1="9" x2="16" y2="15"/>
      <line x1="18" y1="9" x2="18" y2="15"/>
      <line x1="20" y1="9" x2="20" y2="15"/>
      <!-- Brake hose nipple -->
      <line x1="22.5" y1="12" x2="23.6" y2="12"/>
    </svg>`;

/**
 * Brake pad — line icon, modeled on the reference sketch.
 * Two ear-shaped mounting tabs (with bolt holes) on top + curved body with vertical friction grooves.
 */
export const iconBrakePad = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
      <!-- Outer outline: body + two protruding ear tabs -->
      <path d="M3 11
               C 3 9.2 4 8.8 5.2 8.8
               C 6 8.8 6.6 8.8 7 8.8
               C 7 5.8 7.9 4.2 9 4.2
               C 10.1 4.2 11 5.8 11 8.8
               L 13 8.8
               C 13 5.8 13.9 4.2 15 4.2
               C 16.1 4.2 17 5.8 17 8.8
               C 17.4 8.8 18 8.8 18.8 8.8
               C 20 8.8 21 9.2 21 11
               L 20.6 14
               C 20.2 16.6 18.6 17.2 16.8 17.6
               C 13.5 18.4 10.5 18.4 7.2 17.6
               C 5.4 17.2 3.8 16.6 3.4 14
               Z"/>
      <!-- Bolt holes inside ear tabs -->
      <circle cx="9" cy="6.5" r="0.85"/>
      <circle cx="15" cy="6.5" r="0.85"/>
      <!-- Backing-plate / friction interface -->
      <path d="M3.7 11.2 Q12 12.2 20.3 11.2"/>
      <!-- Vertical friction grooves -->
      <line x1="8" y1="12.5" x2="8" y2="16.7"/>
      <line x1="12" y1="13" x2="12" y2="17.4"/>
      <line x1="16" y1="12.5" x2="16" y2="16.7"/>
    </svg>`;

// ─── Tyre ──────────────────────────────────────────────────────────────────

/** Tyre cross-section — clean concentric circles with tread marks */
export const iconTyre = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="2" x2="12" y2="7"/>
      <line x1="12" y1="17" x2="12" y2="22"/>
      <line x1="2" y1="12" x2="7" y2="12"/>
      <line x1="17" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="4.93" x2="8.46" y2="8.46"/>
      <line x1="15.54" y1="15.54" x2="19.07" y2="19.07"/>
      <line x1="19.07" y1="4.93" x2="15.54" y2="8.46"/>
      <line x1="8.46" y1="15.54" x2="4.93" y2="19.07"/>
    </svg>`;

// ─── Impact / Collision Icons ───────────────────────────────────────────────

/** General collision — two cars meeting head-on from diagonal */
export const iconCollision = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 10h4l2-3h4l2 3h3a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-1l-1 1.5H15v-1h-6v1H7.5L6.5 14H5a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1z" opacity="0.5" transform="translate(12,12) scale(-0.7,0.7) translate(-12,-12)"/>
      <path d="M3 10h4l2-3h4l2 3h3a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-1l-1 1.5H15v-1h-6v1H7.5L6.5 14H5a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1z"/>
      <line x1="11" y1="6" x2="11" y2="4" stroke-width="2.5"/>
      <line x1="13" y1="6" x2="15" y2="4" stroke-width="2.5"/>
      <line x1="9" y1="6" x2="7" y2="4" stroke-width="2.5"/>
    </svg>`;

/** Front impact — car facing arrows pointing into front */
export const iconFrontImpact = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="9" width="14" height="8" rx="2"/>
      <path d="M4 11h-3M1 11l3-3M1 11l3 3"/>
      <circle cx="7.5" cy="17" r="1.5"/>
      <circle cx="14.5" cy="17" r="1.5"/>
      <path d="M10 9 L8 6 L14 6 L12 9"/>
    </svg>`;

/** Rear-end impact — arrow hitting car from behind */
export const iconRearImpact = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="9" width="14" height="8" rx="2"/>
      <path d="M20 11h3M23 11l-3-3M23 11l-3 3"/>
      <circle cx="9.5" cy="17" r="1.5"/>
      <circle cx="16.5" cy="17" r="1.5"/>
      <path d="M14 9 L12 6 L18 6 L16 9"/>
    </svg>`;

/** Side impact — arrow hitting car from the side */
export const iconSideImpact = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="5" y="8" width="14" height="8" rx="2"/>
      <path d="M12 8V5M12 5l-3 3M12 5l3 3"/>
      <circle cx="8" cy="16" r="1.5"/>
      <circle cx="16" cy="16" r="1.5"/>
    </svg>`;

/** Rollover — car rotating */
export const iconRollover = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21.5 2v6h-6"/>
      <path d="M21.34 15.57a10 10 0 1 1-.57-8.38"/>
      <rect x="8" y="9" width="8" height="5" rx="1.5" transform="rotate(30 12 11.5)"/>
    </svg>`;

/** Pedestrian involved */
export const iconPedestrian = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="4" r="2"/>
      <path d="M10 22l1.5-6-2.5-3 3-4.5"/>
      <path d="M14 22l-1.5-6 2.5-3-3-4.5"/>
      <path d="M7 14l2-2"/>
      <path d="M17 14l-2-2"/>
    </svg>`;

// ─── AI / Intelligence ──────────────────────────────────────────────────────

/** AI sparkle — elegant AI indicator */
export const iconAI = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
    </svg>`;

// ─── Blackbox status ────────────────────────────────────────────────────────

/** Elegant tick in circle for blackbox active */
export const iconBlackboxActive = () =>
    `<span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-500/50"><svg class="w-3 h-3 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>`;

/** Elegant X in circle for no blackbox */
export const iconBlackboxNone = () =>
    `<span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-slate-700/60 border border-slate-600/50"><svg class="w-3 h-3 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>`;

// ─── Manufacturer Logos ─────────────────────────────────────────────────────
// Authentic brand SVGs live under /static/img/logos/<key>.svg.
// To add a new brand, drop a file in that folder and add its key here.

const MFR_LOGO_FILES = new Set([
    'abarth', 'alfa', 'audi', 'bmw', 'dacia', 'ferrari', 'fiat', 'ford',
    'hyundai', 'kia', 'lamborghini', 'maserati', 'mercedes', 'opel', 'peugeot',
    'porsche', 'renault', 'skoda', 'smart', 'tesla', 'toyota', 'volkswagen', 'volvo',
]);

// Aliases map normalised (lowercase) manufacturer strings → logo file keys.
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
    // Try matching a prefix (e.g. "Mercedes-Benz GLC" → "mercedes")
    for (const key of MFR_LOGO_FILES) {
        if (lower.startsWith(key)) return key;
    }
    for (const [alias, target] of Object.entries(MFR_ALIASES)) {
        if (lower.startsWith(alias)) return target;
    }
    return '';
}

/**
 * Render the authentic manufacturer logo from /static/img/logos/.
 * Falls back to an initials chip if the brand isn't bundled.
 * `size` ∈ {'xs','sm','md','lg'}.
 */
export function manufacturerBadge(manufacturer, size = 'sm') {
    const dimMap = {
        xs: 'w-5 h-5',
        sm: 'w-7 h-7',
        md: 'w-9 h-9',
        lg: 'w-12 h-12',
    };
    const dim = dimMap[size] || dimMap.sm;
    const key = normalizeMfr(manufacturer);
    if (key) {
        return `<span class="${dim} inline-flex items-center justify-center shrink-0" title="${manufacturer || ''}"><img src="/static/img/logos/${key}.svg?v=17" alt="${manufacturer || ''}" class="w-full h-full object-contain" loading="lazy"/></span>`;
    }
    const initials = (manufacturer || '??').replace(/[^A-Za-z]/g, '').substring(0, 2).toUpperCase();
    return `<span class="${dim} rounded-md flex items-center justify-center font-black tracking-tight bg-slate-700/70 border border-slate-500/40 text-slate-200 text-[10px] shrink-0" title="${manufacturer || ''}">${initials}</span>`;
}

// Alias for callers that want to be explicit about "this returns a real logo, not a badge".
export const manufacturerLogo = manufacturerBadge;

// ─── Powertrain badge helper ────────────────────────────────────────────────

export function powertrainIcon(powertrain, cls = 'w-4 h-4') {
    if (!powertrain) return '';
    const pt = powertrain.toLowerCase();
    if (pt === 'electric') return `<span class="text-emerald-400" title="Electric">${iconElectric(cls)}</span>`;
    if (pt.includes('hybrid')) return `<span class="text-blue-400" title="Hybrid">${iconHybrid(cls)}</span>`;
    return `<span class="text-slate-400" title="Petrol/Diesel">${iconPetrol(cls)}</span>`;
}

// ─── Incident type icons ────────────────────────────────────────────────────

export function incidentIcon(type, cls = 'w-4 h-4') {
    const map = {
        collision:    iconCollision,
        rear_end:     iconRearImpact,
        side_impact:  iconSideImpact,
        rollover:     iconRollover,
        pedestrian:   iconPedestrian,
    };
    const fn = map[type] || iconCollision;
    return fn(cls);
}

// ─── Component icons ────────────────────────────────────────────────────────

export function componentIcon(category, cls = 'w-4 h-4') {
    if (category === 'tire')              return iconTyre(cls);
    if (category === 'brake_pad')         return iconBrakePad(cls);
    if (category === 'brake_disc')        return iconBrakeDisc(cls);
    if (category === 'ev_battery')        return iconBattery(cls);
    if (category === 'suspension_damper') return iconSuspensionDamper(cls);
    if (category === 'aux_12v_battery')   return iconAuxBattery(cls);
    if (category === 'engine_oil')        return iconEngineOil(cls);
    if (category === 'dpf')               return iconDpf(cls);
    // fallback
    return `<i data-lucide="settings-2" class="${cls}"></i>`;
}
