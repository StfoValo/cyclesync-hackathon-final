// ==========================================
// INTERNATIONALIZATION (i18n) ENGINE
// ==========================================

window.translations = {
    en: {
        // Landing Page
        "hero-title": "The Digital Product Passport <br /> <span class='text-brand-400 glow-text'>for Next-Gen InsurTech.</span>",
        "hero-subtitle": "Eradicating claims leakage, automating RCA/CASKO adjudication, and unlocking the circular economy through immutable telemetry and AI visual triage.",
        "hero-circularity": "Empowering adjusters with <strong class='text-white'>cryptographic technical proof.</strong>",
        "discover": "Discover",
        "industry-crisis": "The Industry <span class='text-rose-500'>Crisis.</span>",
        "crisis-1-title": "Claims Leakage & Fraud",
        "crisis-1-desc": "Mechanic markups and out-of-network repairs cost insurers millions. Adjusters lack the pre-crash data needed to prove that a claimed €14,000 radiator replacement is actually fraudulent.",
        "crisis-2-title": "The Litigation Trap",
        "crisis-2-desc": "Almost 41% of IVASS complaints result in insurers altering their stance due to a lack of 'technical proof.' Enforcing RCA subrogation (Rivalsa) or denying CASKO claims requires immutable data we currently lack.",
        "crisis-3-title": "The ESG Black Hole",
        "crisis-3-desc": "End-of-life component disposal is entirely disconnected from the insurance lifecycle, making circular economy tracking a regulatory and logistical nightmare.",
        "connected-ecosystem": "The Anti-Fraud <span class='text-brand-500'>Ecosystem.</span>",
        "ecosystem-1-title": "VSI Telemetry",
        "ecosystem-1-desc": "Ingest live telemetry to detect component wear, acting as an immutable audit trail prior to crashes.",
        "ecosystem-2-title": "Proactive Steering",
        "ecosystem-2-desc": "Push alerts to the Driver App, steering users strictly into affiliated, cost-controlled mechanic networks.",
        "ecosystem-3-title": "VeriVision CNN",
        "ecosystem-3-desc": "AI computer vision instantly cross-references mechanic photos against telemetry to block fraudulent payouts.",
        "ecosystem-4-title": "Automated Rivalsa",
        "ecosystem-4-desc": "Provide adjusters with the legal, technical proof required to deny CASKO claims or initiate RCA Subrogation.",
        "btn-enterprise": "Adjuster Portal",
        "btn-enterprise-sub": "Enterprise Dashboard",
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
        "chart-reg-claims": "Registered Claims (Historical)",
        "chart-proj-claims": "Projected Claims (AI Forecast)",
        // Chart Labels (Demographics)
        "chart-age-1": "18-24",
        "chart-age-2": "25-34",
        "chart-age-3": "35-44",
        "chart-age-4": "45-54",
        "chart-age-5": "55-64",
        "chart-age-6": "65+",
        "chart-gender-Male": "Male",
        "chart-gender-Female": "Female",
        "chart-veh-UTILITARIAN": "Compact",
        "chart-veh-HATCHBACK": "Hatchback",
        "chart-veh-SEDAN": "Sedan",
        "chart-veh-SUV": "SUV",
        "chart-veh-SPORTSCAR": "Luxury/Sports",
        "chart-beh-Safe (Eco)": "Low Risk (Eco)",
        "chart-beh-Moderate": "Standard",
        "chart-beh-High Risk (Harsh)": "High Risk",
        "chart-vehage-0-2 Years (New)": "0-2 Years",
        "chart-vehage-3-5 Years (Recent)": "3-5 Years",
        "chart-vehage-6-9 Years (Average)": "6-9 Years",
        "chart-vehage-10+ Years (Old)": "10+ Years",

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
        "adj-search": "Search / Fetch Data",
        "adj-id": "Vehicle Identity",
        "adj-pol-type": "Policy Type:",
        "adj-pol-casko": "CASKO (Comprehensive)",
        "adj-pol-rca": "RCA (Third-Party Liability)",
        "adj-state": "Pre-Crash Telemetry State",
        "adj-brakes": "Brake Assembly",
        "adj-tires": "Tire Tread",
        "adj-batt": "EV Battery",
        "adj-critical": "Critical Wear",
        "adj-warn": "Warning Level",
        "adj-ok": "Healthy",
        "adj-audit": "Immutable Audit Trail",

        // Scenario 1 (CASKO Negligence)
        "adj-opt-fraud": "AB 123 CD - CASKO: Driver Negligence (Denial)",
        "adj-event-1": "VSI detects abnormal tire degradation (below 3mm CASKO limit).",
        "adj-event-2": "Push notification sent to Driver App (Action Required).",
        "adj-event-3": "Driver manually dismissed maintenance alert.",
        "adj-event-4": "Collision reported. Telemetry locked.",
        "adj-ai-title": "VeriTwin AI Adjudicator",
        "adj-ai-desc": "CASKO claim denial recommended. Telemetry proves the vehicle was operating with tires below the 3mm contractual limit. The driver explicitly dismissed alerts prior to the crash. Under CASKO terms, driver negligence voids own-damage coverage.",
        "adj-btn-deny": "Deny CASKO Claim",
        "adj-btn-investigate": "Investigate Further",

        // Scenario 2 (CASKO Good Driver)
        "adj-opt-good": "EF 456 GH - CASKO: Virtuous Driver (Approval)",
        "adj-good-score": "85/100 (HEALTHY)",
        "adj-good-event-1": "Routine monthly VSI diagnostic completed.",
        "adj-good-event-2": "All systems report nominal operation.",
        "adj-good-event-3": "Collision reported. Telemetry locked.",
        "adj-good-ai": "CASKO claim approval recommended. Telemetry confirms safe driving and excellent vehicle maintenance prior to the incident. No mechanical negligence detected.",
        "adj-btn-approve": "Approve Claim",
        "adj-btn-fasttrack": "Fast-Track Payout",

        // Scenario 3 (RCA Rivalsa)
        "adj-opt-defect": "XY 789 ZZ - RCA: Gross Negligence (Rivalsa)",
        "adj-defect-score": "12/100 (CRITICAL)",
        "adj-defect-batt": "Healthy",
        "adj-defect-event-1": "Critical brake failure imminent. VSI score drops below 20.",
        "adj-defect-event-2": "Final automated warning sent to driver.",
        "adj-defect-event-3": "Driver ignores warning. Continues driving.",
        "adj-defect-event-4": "Severe rear-end collision reported. Telemetry locked.",
        "adj-defect-ai": "Third-party payout authorized under mandatory RCA law. However, telemetry proves gross negligence (15% brake capacity ignored for 2 weeks). Initiate 'Rivalsa' (Subrogation) to recover full claim costs from the policyholder.",
        "adj-btn-subrogate": "Initiate Rivalsa against Driver",

        // VeriVision Modal (General & Scenario 1 - Radiator)
        "adj-btn-vision": "👁️ Esegui Triage Visivo VeriVision",
        "cv-title": "Triage CNN VeriVision",
        "cv-mech-claim": "Richiesta Meccanico:",
        "cv-mech-val": "Gruppo Radiatore Anteriore - €14.000",
        "cv-ai-analysis": "Analisi Visiva IA:",
        "cv-ai-val": "0% Danni Strutturali. Componente intatto.",
        "cv-fraud-risk": "Probabilità di Frode:",
        "cv-fraud-val": "98% (CRITICO)",
        "cv-desc": "⚠️ ALLERTA FRODE: L'evidenza visiva contraddice esplicitamente la richiesta di €14.000 del meccanico. L'IA conferma che il radiatore e i supporti strutturali sono intatti. La telemetria conferma un impatto a bassa velocità (< 10km/h). Raccomandazione: Bloccare immediatamente il pagamento.",
        "cv-close": "Chiudi Scansione",

        // VeriVision - Good Driver (Scenario 2 - Bumper)
        "cv-good-mech-claim": "Sostituzione Paraurti Anteriore - €1.200",
        "cv-good-ai-val": "Il profilo del danno corrisponde ai dati di impatto.",
        "cv-good-fraud-val": "4% (SICURO)",
        "cv-good-desc": "✅ VERIFICATO: L'evidenza visiva corrisponde al referto di collisione e alla telemetria. Il danno è isolato alla zona d'impatto senza condizioni preesistenti. Pagamento approvato.",

        // VeriVision - RCA Negligence (Scenario 3 - Brakes)
        "cv-defect-mech-claim": "Guasto Freni - €8.500 (Pagamento Terzi)",
        "cv-defect-ai-val": "0% Materiale d'attrito. Grave rigatura del disco.",
        "cv-defect-fraud-val": "95% (GRAVE NEGLIGENZA)",
        "cv-defect-desc": "⚠️ ALLERTA RIVALSA: La scansione visiva del gruppo freni mostra l'esaurimento completo del materiale d'attrito e rigature metallo su metallo. Questo conferma la telemetria: il conducente ha ignorato l'usura critica per settimane. Procedere con la rivalsa.",

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
        // Landing Page
        "hero-title": "Il Digital Product Passport <br /> <span class='text-brand-400 glow-text'>per l'InsurTech.</span>",
        "hero-subtitle": "Sradicare le frodi, automatizzare l'adjudication RCA/CASKO e sbloccare l'economia circolare tramite telemetria immutabile e triage visivo IA.",
        "hero-circularity": "Forniamo ai periti <strong class='text-white'>prove tecniche inconfutabili.</strong>",
        "discover": "Scopri",
        "industry-crisis": "La Crisi del <span class='text-rose-500'>Settore.</span>",
        "crisis-1-title": "Frodi e Dispersioni",
        "crisis-1-desc": "I ricarichi dei meccanici fuori rete costano milioni alle compagnie. I periti non hanno i dati pre-sinistro per dimostrare che una richiesta di 14.000€ per un radiatore è in realtà una truffa.",
        "crisis-2-title": "La Trappola dei Contenziosi",
        "crisis-2-desc": "Quasi il 41% dei reclami IVASS porta le compagnie a modificare la propria posizione per mancanza di 'prove tecniche'. Applicare la Rivalsa RCA o negare la CASKO richiede dati immutabili.",
        "crisis-3-title": "Il Buco Nero ESG",
        "crisis-3-desc": "Lo smaltimento dei componenti a fine vita è completamente scollegato dal ciclo assicurativo, rendendo il tracciamento per l'economia circolare un incubo normativo.",
        "connected-ecosystem": "L'Ecosistema <span class='text-brand-500'>Anti-Frode.</span>",
        "ecosystem-1-title": "Telemetria VSI",
        "ecosystem-1-desc": "Acquisisci la telemetria in tempo reale per rilevare l'usura, agendo come registro immutabile prima dei sinistri.",
        "ecosystem-2-title": "Indirizzamento Rete",
        "ecosystem-2-desc": "Invia avvisi all'App Guidatore, indirizzando gli utenti esclusivamente verso reti di meccanici convenzionati (es. UnipolService).",
        "ecosystem-3-title": "VeriVision CNN",
        "ecosystem-3-desc": "La computer vision IA incrocia istantaneamente le foto dei meccanici con la telemetria per bloccare i pagamenti fraudolenti.",
        "ecosystem-4-title": "Rivalsa Automatica",
        "ecosystem-4-desc": "Fornisce ai periti la prova tecnica legale necessaria per negare i sinistri CASKO o avviare l'azione di Rivalsa RCA.",
        "btn-enterprise": "Portale Perito",
        "btn-enterprise-sub": "Dashboard Enterprise",
        "btn-driver": "Hub Guidatore",
        "btn-driver-sub": "App Mobile Consumer",

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
        "chart-reg-claims": "Sinistri Registrati (Storico)",
        "chart-proj-claims": "Sinistri Proiettati (Previsione IA)",
        // Chart Labels (Demographics)
        "chart-age-1": "18-24",
        "chart-age-2": "25-34",
        "chart-age-3": "35-44",
        "chart-age-4": "45-54",
        "chart-age-5": "55-64",
        "chart-age-6": "65+",
        "chart-gender-Male": "Uomo",
        "chart-gender-Female": "Donna",
        "chart-veh-UTILITARIAN": "Utilitaria",
        "chart-veh-HATCHBACK": "Hatchback",
        "chart-veh-SEDAN": "Berlina",
        "chart-veh-SUV": "SUV",
        "chart-veh-SPORTSCAR": "Lusso/Sportiva",
        "chart-beh-Safe (Eco)": "Rischio Basso (Eco)",
        "chart-beh-Moderate": "Standard",
        "chart-beh-High Risk (Harsh)": "Rischio Alto",
        "chart-vehage-0-2 Years (New)": "0-2 Anni",
        "chart-vehage-3-5 Years (Recent)": "3-5 Anni",
        "chart-vehage-6-9 Years (Average)": "6-9 Anni",
        "chart-vehage-10+ Years (Old)": "10+ Anni",

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
        "adj-search": "Cerca / Estrai Dati",
        "adj-id": "Identità Veicolo",
        "adj-pol-type": "Tipo Polizza:",
        "adj-pol-casko": "CASKO (Danni Propri)",
        "adj-pol-rca": "RCA (Responsabilità Civile)",
        "adj-state": "Stato Telemetria Pre-Sinistro",
        "adj-brakes": "Sistema Frenante",
        "adj-tires": "Battistrada Pneumatici",
        "adj-batt": "Batteria EV",
        "adj-critical": "Usura Critica",
        "adj-warn": "Livello di Avviso",
        "adj-ok": "In Salute",
        "adj-audit": "Registro Audit Immutabile",

        // Scenario 1 (CASKO Negligence)
        "adj-opt-fraud": "AB 123 CD - CASKO: Negligenza Guidatore (Rifiuto)",
        "adj-event-1": "Rilevato degrado pneumatici (sotto limite CASKO 3mm).",
        "adj-event-2": "Notifica push inviata all'App Guidatore (Azione Richiesta).",
        "adj-event-3": "Il guidatore ha ignorato l'avviso di manutenzione.",
        "adj-event-4": "Sinistro segnalato. Telemetria bloccata.",
        "adj-ai-title": "Adjudicator AI VeriTwin",
        "adj-ai-desc": "Si raccomanda il rifiuto del sinistro CASKO. La telemetria prova che il veicolo operava con pneumatici sotto il limite contrattuale di 3mm. Il conducente ha ignorato gli avvisi. Secondo le condizioni CASKO, la negligenza annulla la copertura per danni propri.",
        "adj-btn-deny": "Rifiuta Sinistro CASKO",
        "adj-btn-investigate": "Indaga Oltre",

        // Scenario 2 (CASKO Good Driver)
        "adj-opt-good": "EF 456 GH - CASKO: Guidatore Virtuoso (Approvazione)",
        "adj-good-score": "85/100 (SANO)",
        "adj-good-event-1": "Diagnostica mensile di routine VSI completata.",
        "adj-good-event-2": "Tutti i sistemi segnalano un funzionamento nominale.",
        "adj-good-event-3": "Sinistro segnalato. Telemetria bloccata.",
        "adj-good-ai": "Approvazione sinistro CASKO raccomandata. La telemetria conferma una guida sicura e un'eccellente manutenzione del veicolo prima dell'incidente. Nessuna negligenza meccanica rilevata.",
        "adj-btn-approve": "Approva Sinistro",
        "adj-btn-fasttrack": "Pagamento Rapido (Fast-Track)",

        // Scenario 3 (RCA Rivalsa)
        "adj-opt-defect": "XY 789 ZZ - RCA: Negligenza Grave (Rivalsa)",
        "adj-defect-score": "12/100 (CRITICO)",
        "adj-defect-batt": "In Salute",
        "adj-defect-event-1": "Guasto critico ai freni imminente. Punteggio VSI sotto 20.",
        "adj-defect-event-2": "Ultimo avviso automatico inviato al guidatore.",
        "adj-defect-event-3": "Il guidatore ignora l'avviso e continua a guidare.",
        "adj-defect-event-4": "Grave tamponamento segnalato. Telemetria bloccata.",
        "adj-defect-ai": "Pagamento al terzo autorizzato come previsto dalla legge RCA. Tuttavia, la telemetria prova grave negligenza (freni al 15% ignorati per 2 settimane). Avviare 'Rivalsa' per recuperare i costi totali del sinistro dall'assicurato.",
        "adj-btn-subrogate": "Avvia Rivalsa contro Assicurato",

        // VeriVision Modal (General & Scenario 1 - Radiator)
        "adj-btn-vision": "👁️ Esegui Triage Visivo VeriVision",
        "cv-title": "Triage CNN VeriVision",
        "cv-mech-claim": "Richiesta Meccanico:",
        "cv-mech-val": "Gruppo Radiatore Anteriore - €14.000",
        "cv-ai-analysis": "Analisi Visiva IA:",
        "cv-ai-val": "0% Danni Strutturali. Componente intatto.",
        "cv-fraud-risk": "Probabilità di Frode:",
        "cv-fraud-val": "98% (CRITICO)",
        "cv-desc": "⚠️ ALLERTA FRODE: L'evidenza visiva contraddice esplicitamente la richiesta di €14.000 del meccanico. L'IA conferma che il radiatore e i supporti strutturali sono intatti. La telemetria conferma un impatto a bassa velocità (< 10km/h). Raccomandazione: Bloccare immediatamente il pagamento.",
        "cv-close": "Chiudi Scansione",

        // VeriVision - Good Driver (Scenario 2 - Bumper)
        "cv-good-mech-claim": "Sostituzione Paraurti Anteriore - €1.200",
        "cv-good-ai-val": "Il profilo del danno corrisponde ai dati di impatto.",
        "cv-good-fraud-val": "4% (SICURO)",
        "cv-good-desc": "✅ VERIFICATO: L'evidenza visiva corrisponde al referto di collisione e alla telemetria. Il danno è isolato alla zona d'impatto senza condizioni preesistenti. Pagamento approvato.",

        // VeriVision - RCA Negligence (Scenario 3 - Brakes)
        "cv-defect-mech-claim": "Guasto Freni - €8.500 (Pagamento Terzi)",
        "cv-defect-ai-val": "0% Materiale d'attrito. Grave rigatura del disco.",
        "cv-defect-fraud-val": "95% (GRAVE NEGLIGENZA)",
        "cv-defect-desc": "⚠️ ALLERTA RIVALSA: La scansione visiva del gruppo freni mostra l'esaurimento completo del materiale d'attrito e rigature metallo su metallo. Questo conferma la telemetria: il conducente ha ignorato l'usura critica per settimane. Procedere con la rivalsa.",

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
    localStorage.setItem('veritwin_lang', lang);

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