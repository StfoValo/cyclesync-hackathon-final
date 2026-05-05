// ==========================================
// INTERNATIONALIZATION (i18n) ENGINE
// ==========================================

window.translations = {
    en: {
        // Landing & General
        "hero-title": "The Sustainability <br /> <span class='text-brand-400 glow-text'>Digital Twin.</span>",
        "hero-subtitle": "Bridging the gap between a vehicle's birth, life, and second life. Moving the automotive industry beyond 'replace-by-default'.",
        "hero-circularity": "Unlocking the <strong>Circularity Value Chain</strong>",
        "discover": "Discover",
        "industry-crisis": "The Industry <span class='text-rose-500'>Crisis.</span>",
        "crisis-1-title": "30% Cost Premium",
        "crisis-1-desc": "When drivers use out-of-network mechanics, insurers lose visibility on parts and labor, resulting in maintenance costs that are consistently <strong class='text-rose-400 font-semibold'>30% higher</strong>.",
        "crisis-2-title": "Death of the Black Box",
        "crisis-2-desc": "Traditional aftermarket telematics revenue is plummeting. OEMs are embedding sensors natively, and new strict <strong class='text-rose-400 font-semibold'>data regulations</strong> are killing the legacy market.",
        "crisis-3-title": "An ESG Black Hole",
        "crisis-3-desc": "End-of-life material disposal documentation is <strong class='text-rose-400 font-semibold'>scattered and untraceable</strong>, making circular economy tracking a regulatory nightmare.",
        "connected-ecosystem": "The Connected <span class='text-brand-500'>Ecosystem.</span>",
        "ecosystem-1-title": "Predictive Models",
        "ecosystem-1-desc": "Ingest telematics to accurately detect component wear and hardware risk.",
        "ecosystem-2-title": "Maintenance Alerts",
        "ecosystem-2-desc": "Push proactive intervention alerts directly to the driver's mobile app.",
        "ecosystem-3-title": "Dynamic Pricing",
        "ecosystem-3-desc": "Reward good behavior by offering targeted discounts for prompt repairs.",
        "ecosystem-4-title": "Affiliated Network",
        "ecosystem-4-desc": "Drive traffic exclusively to trusted workshops, locking in savings.",
        "ecosystem-slogan": "Lower risk. Fewer claims. Happier customers.",
        "closing-loop": "Closing the Circular Economy Loop",
        "loop-1-title": "1. Birth",
        "loop-1-desc": "Ingesting fragmented OEM factory blueprints and supply chain composition data.",
        "loop-2-title": "2. Life",
        "loop-2-desc": "Monitoring real-world driver behavior via VSI telemetry to build risk profiles.",
        "loop-3-title": "3. Second Life",
        "loop-3-desc": "Deploying AI to intelligently triage End-of-Life parts for raw material extraction.",
        "btn-enterprise": "Enterprise Portal",
        "btn-enterprise-sub": "Insurer & OEM Access",
        "btn-driver": "Driver Hub",
        "btn-driver-sub": "Consumer Mobile App",

        // Dashboard Sidebar
        "nav-driver-app": "🚗 Driver App",
        "nav-fleet": "Fleet Telemetry",
        "nav-risk": "Risk Summary",
        "nav-asset": "Asset Risk",
        "nav-ai": "AI Routing",
        "nav-esg": "ESG & Circular",
        "nav-admin": "Admin",
        "nav-sys-access": "System Access",
        "nav-launch": "Launch Driver App",

        // Partials: Telemetry
        "tel-title": "Live Fleet Telemetry",
        "tel-subtitle": "Real-time geographical tracking and fleet metrics.",
        "tel-btn-live": "Live Monitored Fleet",
        "tel-btn-network": "Conventioned Network",

        // Partials: Executive
        "exec-title": "Executive Risk Summary",
        "exec-subtitle": "Actuarial financial projections and demographic deep dives.",
        "exec-btn-regional": "Regional Overview",
        "exec-btn-demo": "Demographics",
        "exec-kpi-total": "Total Monitored Fleet",
        "exec-kpi-avg": "Avg Premium (EUR)",
        "exec-kpi-disc": "Telematics Discount",
        "exec-kpi-claims": "Claims Reduction",
        "exec-chart-age": "Claims by Driver Age Group",
        "exec-chart-gender": "Claims by Gender",
        "exec-chart-vehicle": "Claims by Vehicle Category",
        "exec-chart-behavior": "Claims by Behavioral Risk",
        "exec-chart-vehage": "Claims by Vehicle Age (Italian RCA)",

        // Partials: Asset
        "asset-title": "Predictive Asset Risk",
        "asset-subtitle": "Vehicle State Index (VSI) and component degradation analytics.",
        "asset-kpi-vsi": "Fleet Average VSI Score",
        "asset-kpi-crit": "Vehicles in Critical State",
        "asset-kpi-hw": "Projected Hardware Claims",
        "asset-chart-vsi": "Regional Fleet Safety Index (VSI) Breakdown",
        "asset-chart-brake": "Regional Brake Pad Degradation Matrix",
        "asset-chart-tire": "Regional Tire Tread Wear Analytics",
        "asset-chart-gvsi": "Global VSI",
        "asset-chart-gbrake": "Global Brakes",
        "asset-chart-gtire": "Global Tires",

        // Chart Labels (Asset & VSI)
        "chart-safe": "Safe (Eco)",
        "chart-warn": "Moderate Risk",
        "chart-crit": "Critical Risk",
        "chart-safe-b": "Healthy (<40% Wear)",
        "chart-warn-b": "Warning (40-80% Wear)",
        "chart-crit-b": "Replace Subito (>80%)",
        "chart-safe-t": "Healthy Tread",
        "chart-warn-t": "Worn Tread",
        "chart-crit-t": "Bald/Illegal Tread",

        // Partials: AI Routing
        "ai-title": "AI Routing Directive",
        "ai-subtitle": "LLM-powered strategic intelligence and policy recommendations.",
        "ai-sel-region": "📍 Select Target Region:",
        "ai-btn-gen": "Generate Strategy",
        "ai-term-title": "Telematics AI",
        "ai-term-now": "Now",
        "ai-term-wait": "Awaiting actuarial input...",
        "ai-funnel-title": "📈 Post-Dispatch Conversion Funnel",
        "ai-kpi-target": "Total Devices Targeted",
        "ai-kpi-open": "Notification Open Rate",
        "ai-kpi-booked": "Repairs Booked (Network)",
        "ai-kpi-roi": "Est. Claims Prevented (ROI)",

        // Partials: ESG
        "esg-title": "ESG & Circular Economy",
        "esg-subtitle": "Virtual emissions sensor and component second-life ledger.",
        "esg-virt-sensor": "Virtual Emissions Sensor",
        "esg-base-co2": "Baseline CO2 (Tons)",
        "esg-real-co2": "Real Telematics CO2 (Tons)",
        "esg-saved-co2": "Total CO2 Saved (Tons)",
        "esg-trees": "Equivalent Trees Planted",
        "esg-ledger": "The Second Life Component Ledger",
        "esg-tires": "Tires Recovered",
        "esg-brakes": "Brake Pads Recovered",
        "esg-batts": "EV Batteries Recovered",
        "esg-triage": "♻️ AI Component Triage & Reverse Logistics",
        "esg-triage-sub": "Bridging Birth, Life, and Second Life.",
        "esg-sel-region": "Select Region",
        "esg-btn-run": "Run Component Triage",
        "esg-step-1": "1. OEM Blueprint Ingestion &rarr;",
        "esg-step-2": "2. Telemetry Wear Analysis &rarr;",
        "esg-step-3": "3. Second-Life Routing",
        "esg-term-wait": "Awaiting regional selection to begin triage...",

        // Chart Labels (ESG)
        "chart-Asphalt": "Asphalt Recycling",
        "chart-Energy": "Energy Recovery",
        "chart-Landfill": "Landfill (Waste)",
        "chart-Scrap": "Scrap Metal Smelting",
        "chart-Friction": "Friction Material",
        "chart-Grid": "Grid Storage",
        "chart-Black": "Black Mass Recycling",
        "chart-Hazardous": "Hazardous Waste",

        // Adjuster Portal
        "nav-adjuster": "Adjuster",
        "adj-title": "Anti-Fraud Adjuster Portal",
        "adj-subtitle": "Digital Product Passport (DPP) & pre-crash telemetry investigation.",
        "adj-search": "Search",
        "adj-id": "Vehicle Identity",
        "adj-state": "Pre-Crash Telemetry State",
        "adj-brakes": "Brake Assembly",
        "adj-tires": "Tire Tread",
        "adj-batt": "EV Battery",
        "adj-critical": "Critical Wear",
        "adj-warn": "Warning Level",
        "adj-ok": "Healthy",
        "adj-audit": "Immutable Audit Trail",
        "adj-event-1": "VSI detects abnormal braking degradation.",
        "adj-event-2": "Push notification sent to Driver App (Action Required).",
        "adj-event-3": "Driver manually dismissed maintenance alert.",
        "adj-event-4": "Collision reported. Telemetry locked.",
        "adj-ai-title": "CycleSync AI Adjudicator",
        "adj-ai-desc": "Claim denial recommended. Immutable telemetry indicates the driver experienced a 45% loss in braking efficiency over 3 weeks and explicitly dismissed 3 critical maintenance alerts prior to the rear-end collision. Liability rests entirely on driver negligence, not sudden mechanical failure.",
        "adj-btn-deny": "Deny Claim",
        "adj-btn-investigate": "Investigate Further",

        // Dropdown Options
        "adj-opt-fraud": "AB 123 CD - Fraud Case / Driver Negligence",
        "adj-opt-good": "EF 456 GH - Virtuous Driver (Instant Approval)",
        "adj-opt-defect": "XY 789 ZZ - OEM Hardware Defect (Subrogation Opportunity)",

        // Driver App
        "driver-hello": "Hi, Andrea",
        "driver-sos": "Quick SOS",
        "driver-parking": "Parking",
        "driver-charging": "EV Charging",
        "driver-action-req": "Action Required",
        "driver-maint-rec": "Recommended Maintenance",
        "driver-maint-desc": "Abnormal brake wear detected. Intervene to maintain your telematics discount.",
        "driver-view-details": "View details &rarr;",
        "driver-active-veh": "Active Vehicle",
        "driver-your-suv": "Your SUV",
        "driver-vsi-score": "VSI Score: Excellent",
        "driver-policy-disc": "Policy Discount",
        "driver-telematics": "Telematics",
        "driver-alert-details": "Alert Details",
        "driver-alert-desc": "We have detected abnormal wear on your brake pads. Intervene to drive safely and gain an advantage on your policy.",
        "driver-discount-active": "Activatable Policy Discount",
        "driver-discount-after": "After the intervention you will receive",
        "driver-risk-red": "Claims Risk Reduction",
        "driver-up-to": "Up to",
        "driver-act-now": "by intervening now",
        "driver-find-shop": "Find affiliated workshop",
        "driver-ignore": "Ignore for now",
        "driver-network": "Affiliated Network",
        "driver-nav-home": "Home",
        "driver-nav-network": "Network",
        "driver-nav-alerts": "Alerts",
        "driver-nav-profile": "Profile",
        "driver-health-title": "Component Health",
        "driver-brakes": "Brake Pads",
        "driver-brakes-warn": "Check required",
        "driver-tires": "Tires",
        "driver-tires-ok": "Optimal",
        "driver-battery": "EV Battery Health",
        "driver-battery-ok": "Healthy",
        "driver-eco-title": "Eco Impact",
        "driver-co2-saved": "CO2 Saved",
        "driver-trees": "Equivalent Trees",
    },
    it: {
        // Landing & General
        "hero-title": "Il <span class='text-brand-400 glow-text'>Digital Twin</span> <br /> della Sostenibilità.",
        "hero-subtitle": "Colmiamo il divario tra la nascita, la vita e la seconda vita di un veicolo. Oltre il concetto di 'sostituzione di default'.",
        "hero-circularity": "Sblocchiamo la <strong>Catena del Valore della Circolarità</strong>",
        "discover": "Scopri",
        "industry-crisis": "La Crisi <span class='text-rose-500'>dell'Industria.</span>",
        "crisis-1-title": "Aumento dei Costi del 30%",
        "crisis-1-desc": "Quando gli automobilisti usano meccanici non convenzionati, le assicurazioni perdono visibilità su ricambi e manodopera, con costi di manutenzione <strong class='text-rose-400 font-semibold'>maggiori del 30%</strong>.",
        "crisis-2-title": "La Fine della Scatola Nera",
        "crisis-2-desc": "I ricavi della telematica aftermarket stanno crollando. Gli OEM integrano i sensori nativamente e le <strong class='text-rose-400 font-semibold'>nuove normative sui dati</strong> stanno uccidendo il mercato tradizionale.",
        "crisis-3-title": "Un Buco Nero ESG",
        "crisis-3-desc": "La documentazione sullo smaltimento a fine vita è <strong class='text-rose-400 font-semibold'>dispersa e non tracciabile</strong>, rendendo l'economia circolare un incubo normativo.",
        "connected-ecosystem": "L'Ecosistema <span class='text-brand-500'>Connesso.</span>",
        "ecosystem-1-title": "Modelli Predittivi",
        "ecosystem-1-desc": "Acquisizione della telematica per rilevare accuratamente l'usura dei componenti e i rischi hardware.",
        "ecosystem-2-title": "Avvisi di Manutenzione",
        "ecosystem-2-desc": "Invio di avvisi di intervento proattivi direttamente sull'app mobile del guidatore.",
        "ecosystem-3-title": "Prezzi Dinamici",
        "ecosystem-3-desc": "Premia il buon comportamento offrendo sconti mirati per riparazioni tempestive.",
        "ecosystem-4-title": "Rete Affiliata",
        "ecosystem-4-desc": "Indirizza il traffico esclusivamente verso officine di fiducia, garantendo risparmi.",
        "ecosystem-slogan": "Meno rischi. Meno sinistri. Clienti più felici.",
        "closing-loop": "Chiudere il Ciclo dell'Economia Circolare",
        "loop-1-title": "1. Nascita",
        "loop-1-desc": "Acquisizione di progetti frammentati dagli OEM e dati sulla composizione della catena di fornitura.",
        "loop-2-title": "2. Vita",
        "loop-2-desc": "Monitoraggio del comportamento di guida reale tramite telemetria VSI per creare profili di rischio.",
        "loop-3-title": "3. Seconda Vita",
        "loop-3-desc": "Uso dell'IA per smistare in modo intelligente i componenti a fine vita per l'estrazione di materie prime.",
        "btn-enterprise": "Portale Enterprise",
        "btn-enterprise-sub": "Accesso Assicurazioni & OEM",
        "btn-driver": "App Guidatore",
        "btn-driver-sub": "App Mobile Utente",

        // Dashboard Sidebar
        "nav-driver-app": "🚗 App Guidatore",
        "nav-fleet": "Telemetria Flotta",
        "nav-risk": "Riepilogo Rischi",
        "nav-asset": "Rischio Asset",
        "nav-ai": "Routing IA",
        "nav-esg": "ESG & Circolare",
        "nav-admin": "Amministratore",
        "nav-sys-access": "Accesso di Sistema",
        "nav-launch": "Avvia App Guidatore",

        // Partials: Telemetry
        "tel-title": "Telemetria Flotta in Tempo Reale",
        "tel-subtitle": "Tracciamento geografico in tempo reale e metriche della flotta.",
        "tel-btn-live": "Flotta Monitorata in Diretta",
        "tel-btn-network": "Rete Convenzionata",

        // Partials: Executive
        "exec-title": "Riepilogo Rischi Esecutivo",
        "exec-subtitle": "Proiezioni finanziarie attuariali e approfondimenti demografici.",
        "exec-btn-regional": "Panoramica Regionale",
        "exec-btn-demo": "Demografia",
        "exec-kpi-total": "Flotta Totale Monitorata",
        "exec-kpi-avg": "Premio Medio (EUR)",
        "exec-kpi-disc": "Sconto Telematica",
        "exec-kpi-claims": "Riduzione Sinistri",
        "exec-chart-age": "Sinistri per Fascia d'Età",
        "exec-chart-gender": "Sinistri per Genere",
        "exec-chart-vehicle": "Sinistri per Categoria Veicolo",
        "exec-chart-behavior": "Sinistri per Rischio Comportamentale",
        "exec-chart-vehage": "Sinistri per Età Veicolo (RCA Italiana)",

        // Partials: Asset
        "asset-title": "Rischio Asset Predittivo",
        "asset-subtitle": "Indice di Stato del Veicolo (VSI) e analisi del degrado dei componenti.",
        "asset-kpi-vsi": "Punteggio VSI Medio Flotta",
        "asset-kpi-crit": "Veicoli in Stato Critico",
        "asset-kpi-hw": "Sinistri Hardware Previsti",
        "asset-chart-vsi": "Ripartizione Regionale Indice Sicurezza Flotta (VSI)",
        "asset-chart-brake": "Matrice Regionale Degrado Pastiglie Freni",
        "asset-chart-tire": "Analisi Regionale Usura Battistrada Pneumatici",
        "asset-chart-gvsi": "VSI Globale",
        "asset-chart-gbrake": "Freni Globali",
        "asset-chart-gtire": "Pneumatici Globali",

        // Chart Labels (Asset & VSI)
        "chart-safe": "Sicuro (Eco)",
        "chart-warn": "Rischio Moderato",
        "chart-crit": "Rischio Critico",
        "chart-safe-b": "Sano (<40% Usura)",
        "chart-warn-b": "Attenzione (40-80% Usura)",
        "chart-crit-b": "Sostituire Subito (>80%)",
        "chart-safe-t": "Battistrada Sano",
        "chart-warn-t": "Battistrada Usurato",
        "chart-crit-t": "Battistrada Illegale",

        // Partials: AI Routing
        "ai-title": "Direttiva di Routing IA",
        "ai-subtitle": "Intelligenza strategica basata su LLM e raccomandazioni di policy.",
        "ai-sel-region": "📍 Seleziona Regione Target:",
        "ai-btn-gen": "Genera Strategia",
        "ai-term-title": "IA Telematica",
        "ai-term-now": "Ora",
        "ai-term-wait": "In attesa di input attuariale...",
        "ai-funnel-title": "📈 Imbuto di Conversione Post-Invio",
        "ai-kpi-target": "Dispositivi Totali Targettizzati",
        "ai-kpi-open": "Tasso di Apertura Notifiche",
        "ai-kpi-booked": "Riparazioni Prenotate (Rete)",
        "ai-kpi-roi": "Sinistri Evitati Stimati (ROI)",

        // Partials: ESG
        "esg-title": "ESG & Economia Circolare",
        "esg-subtitle": "Sensore di emissioni virtuale e registro seconda vita componenti.",
        "esg-virt-sensor": "Sensore di Emissioni Virtuale",
        "esg-base-co2": "CO2 di Base (Tonnellate)",
        "esg-real-co2": "CO2 Telematica Reale (Tonnellate)",
        "esg-saved-co2": "Totale CO2 Risparmiata (Tonnellate)",
        "esg-trees": "Alberi Equivalenti Piantati",
        "esg-ledger": "Il Registro dei Componenti Seconda Vita",
        "esg-tires": "Pneumatici Recuperati",
        "esg-brakes": "Pastiglie Freni Recuperate",
        "esg-batts": "Batterie EV Recuperate",
        "esg-triage": "♻️ Triage Componenti IA & Logistica Inversa",
        "esg-triage-sub": "Colmare il divario tra Nascita, Vita e Seconda Vita.",
        "esg-sel-region": "Seleziona Regione",
        "esg-btn-run": "Esegui Triage Componenti",
        "esg-step-1": "1. Acquisizione Progetti OEM &rarr;",
        "esg-step-2": "2. Analisi Usura Telemetria &rarr;",
        "esg-step-3": "3. Routing Seconda Vita",
        "esg-term-wait": "In attesa di selezione regionale per iniziare il triage...",

        // Chart Labels (ESG)
        "chart-Asphalt": "Riciclo Asfalto",
        "chart-Energy": "Recupero Energetico",
        "chart-Landfill": "Discarica (Scarto)",
        "chart-Scrap": "Fusione Rottami",
        "chart-Friction": "Materiale d'Attrito",
        "chart-Grid": "Accumulo Rete (Grid)",
        "chart-Black": "Riciclo Black Mass",
        "chart-Hazardous": "Rifiuti Pericolosi",

        // Adjuster Portal
        "nav-adjuster": "Perito",
        "adj-title": "Portale Perito Anti-Frode",
        "adj-subtitle": "Digital Product Passport (DPP) e indagine telemetrica pre-sinistro.",
        "adj-search": "Cerca",
        "adj-id": "Identità Veicolo",
        "adj-state": "Stato Telemetria Pre-Sinistro",
        "adj-brakes": "Sistema Frenante",
        "adj-tires": "Battistrada Pneumatici",
        "adj-batt": "Batteria EV",
        "adj-critical": "Usura Critica",
        "adj-warn": "Livello di Avviso",
        "adj-ok": "In Salute",
        "adj-audit": "Registro Audit Immutabile",
        "adj-event-1": "Il VSI rileva un degrado anomalo in frenata.",
        "adj-event-2": "Notifica push inviata all'App Guidatore (Azione Richiesta).",
        "adj-event-3": "Il guidatore ha ignorato manualmente l'avviso di manutenzione.",
        "adj-event-4": "Sinistro segnalato. Telemetria bloccata.",
        "adj-ai-title": "Adjudicator AI CycleSync",
        "adj-ai-desc": "Si raccomanda il rifiuto del sinistro. La telemetria immutabile indica che il conducente ha subito una perdita del 45% dell'efficienza frenante in 3 settimane e ha esplicitamente ignorato 3 avvisi critici prima del tamponamento. La responsabilità ricade interamente sulla negligenza del conducente, non su un guasto meccanico improvviso.",
        "adj-btn-deny": "Rifiuta Sinistro",
        "adj-btn-investigate": "Indaga Oltre",

        "adj-opt-fraud": "AB 123 CD - Caso Frode / Negligenza Guidatore",
        "adj-opt-good": "EF 456 GH - Guidatore Virtuoso (Approvazione Istantanea)",
        "adj-opt-defect": "XY 789 ZZ - Difetto Hardware OEM (Azione di Rivalsa)",

        // Driver App
        "driver-hello": "Ciao, Andrea",
        "driver-sos": "Soccorso Rapido",
        "driver-parking": "Parcheggi",
        "driver-charging": "Ricarica EV",
        "driver-action-req": "Azione Richiesta",
        "driver-maint-rec": "Manutenzione Consigliata",
        "driver-maint-desc": "Rilevata usura anomala freni. Intervieni per mantenere lo sconto telematica.",
        "driver-view-details": "Vedi dettagli &rarr;",
        "driver-active-veh": "Veicolo Attivo",
        "driver-your-suv": "Il tuo SUV",
        "driver-vsi-score": "VSI Score: Ottimo",
        "driver-policy-disc": "Sconto Polizza",
        "driver-telematics": "Telematica",
        "driver-alert-details": "Dettagli Avviso",
        "driver-alert-desc": "Abbiamo rilevato un'usura anomala delle pastiglie dei freni. Intervieni per guidare in sicurezza e ottenere un vantaggio sulla tua polizza.",
        "driver-discount-active": "Sconto polizza attivabile",
        "driver-discount-after": "Dopo l'intervento riceverai",
        "driver-risk-red": "Riduzione rischio sinistri",
        "driver-up-to": "Fino a",
        "driver-act-now": "intervenendo ora",
        "driver-find-shop": "Trova officina convenzionata",
        "driver-ignore": "Ignora per ora",
        "driver-network": "Rete Convenzionata",
        "driver-nav-home": "Home",
        "driver-nav-network": "Network",
        "driver-nav-alerts": "Avvisi",
        "driver-nav-profile": "Profilo",
        "driver-health-title": "Stato Componenti",
        "driver-brakes": "Pastiglie Freni",
        "driver-brakes-warn": "Controllo richiesto",
        "driver-tires": "Pneumatici",
        "driver-tires-ok": "Ottimale",
        "driver-battery": "Stato Batteria EV",
        "driver-battery-ok": "In salute",
        "driver-eco-title": "Impatto Eco",
        "driver-co2-saved": "CO2 Risparmiata",
        "driver-trees": "Alberi Equivalenti",
    }
};

window.setLanguage = function (lang) {
    localStorage.setItem('cyclesync_lang', lang);

    // Grab Desktop Buttons
    const btnEn = document.getElementById('lang-en');
    const btnIt = document.getElementById('lang-it');

    // Grab Mobile App Buttons
    const btnEnApp = document.getElementById('lang-en-app');
    const btnItApp = document.getElementById('lang-it-app');

    const activeClass = "px-3 py-1.5 md:px-3 md:py-1.5 px-2.5 py-1 rounded-full text-[10px] md:text-xs font-bold transition-all bg-brand-500 text-slate-900 shadow-[0_0_10px_rgba(0,229,255,0.4)]";
    const inactiveClass = "px-3 py-1.5 md:px-3 md:py-1.5 px-2.5 py-1 rounded-full text-[10px] md:text-xs font-bold transition-all text-slate-400 hover:text-white bg-transparent shadow-none";

    if (lang === 'en') {
        if (btnEn) btnEn.className = activeClass;
        if (btnEnApp) btnEnApp.className = activeClass;
        if (btnIt) btnIt.className = inactiveClass;
        if (btnItApp) btnItApp.className = inactiveClass;
    } else {
        if (btnIt) btnIt.className = activeClass;
        if (btnItApp) btnItApp.className = activeClass;
        if (btnEn) btnEn.className = inactiveClass;
        if (btnEnApp) btnEnApp.className = inactiveClass;
    }

    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (window.translations[lang] && window.translations[lang][key]) {
            element.innerHTML = window.translations[lang][key];
        }
    });

    if (window.Chart && window.Chart.instances) {
        Object.values(window.Chart.instances).forEach(chart => { chart.update(); });
    }
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
};