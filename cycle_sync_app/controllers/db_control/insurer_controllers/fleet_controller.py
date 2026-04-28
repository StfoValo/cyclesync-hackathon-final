import json
from PyQt6.QtCore import QObject
from mcp_agent_server.ai_orchestrator import AIOrchestrator

class FleetController(QObject):

    # --- UNIPOL CONVENTIONED NETWORK ---
    SERVICE_PROVIDERS = [
        {"name": "Autofficina Sprint", "type": "Officina", "lat": 45.5421, "lon": 9.2014, "region": "Lombardia"},
        {"name": "Pneus Master", "type": "Gommista", "lat": 41.8905, "lon": 12.4942, "region": "Lazio"},
        {"name": "Meccanica Elite", "type": "Officina", "lat": 37.5013, "lon": 15.0742, "region": "Sicilia"},
        {"name": "Garage Centrale", "type": "Officina", "lat": 40.8522, "lon": 14.2681, "region": "Campania"},
        {"name": "Tutto Gomme Nord", "type": "Gommista", "lat": 45.4381, "lon": 12.3185, "region": "Veneto"},
        {"name": "RiparaAuto 24h", "type": "Officina", "lat": 44.4949, "lon": 11.3426, "region": "Emilia-Romagna"},
        {"name": "Wheel Center Advanced", "type": "Gommista", "lat": 45.0703, "lon": 7.6869, "region": "Piemonte"},
        {"name": "Officina del Sole", "type": "Officina", "lat": 41.1171, "lon": 16.8719, "region": "Puglia"},
        {"name": "Pneus Express", "type": "Gommista", "lat": 43.7696, "lon": 11.2558, "region": "Toscana"},
        {"name": "Carrozzeria Sud", "type": "Officina", "lat": 38.9054, "lon": 16.5873, "region": "Calabria"},
        {"name": "Battistrada Sicuro", "type": "Gommista", "lat": 39.2238, "lon": 9.1217, "region": "Sardegna"},
        {"name": "Service Rossi", "type": "Officina", "lat": 43.6158, "lon": 13.5189, "region": "Marche"},
        {"name": "Officina Adriatica", "type": "Officina", "lat": 42.4618, "lon": 14.2161, "region": "Abruzzo"},
        {"name": "Gomme & Co. Elite", "type": "Gommista", "lat": 46.0711, "lon": 13.2373, "region": "Friuli-Venezia Giulia"},
        {"name": "Meccanica Ligure", "type": "Officina", "lat": 44.4056, "lon": 8.9463, "region": "Liguria"},
        {"name": "Alpina Service", "type": "Officina", "lat": 46.0679, "lon": 11.1211, "region": "Trentino-Alto Adige"},
        {"name": "Pneus Umbria", "type": "Gommista", "lat": 43.1107, "lon": 12.3908, "region": "Umbria"},
        {"name": "Lucania Motors", "type": "Officina", "lat": 40.6333, "lon": 15.8000, "region": "Basilicata"},
        {"name": "Molise Gomme", "type": "Gommista", "lat": 41.5603, "lon": 14.6599, "region": "Molise"},
        {"name": "Garage Monte Bianco", "type": "Officina", "lat": 45.7373, "lon": 7.3201, "region": "Valle d'Aosta"}
    ]

    def __init__(self, map_view, ai_dashboard_view, model, account_id):
        super().__init__()
        self.map_view = map_view            
        self.ai_view = ai_dashboard_view    
        self.model = model
        self.account_id = account_id
        
        self.agent = AIOrchestrator()
        
        # Wire UI logic
        self.ai_view.btn_request_ai_analysis.clicked.connect(self.trigger_ai_agent)
        self.map_view.simulate_requested.connect(self.run_simulation)
        self.map_view.view_toggle.currentItemChanged.connect(self.load_fleet_data)
        
        self.load_fleet_data()
        self.refresh_ai_dashboard_visuals()

    def run_simulation(self):
        """Triggers the Monte Carlo simulation and refreshes both UIs."""
        # 1. Tell the model to generate the new cars
        self.model.simulate_regional_fleet(self.account_id)
        
        # 2. Refresh the Map View
        self.load_fleet_data()
        
        # 3. Refresh the AI Dashboard Histogram
        self.refresh_ai_dashboard_visuals()

    def load_fleet_data(self, *args):
        """Passes both the fleet data and the supplier data to the map."""
        fleet_data = self.model.get_regional_kpis(self.account_id)
        
        active_view = 'fleet' 
        if args and isinstance(args[0], str):
            active_view = args[0]
        else:
            current_item = self.map_view.view_toggle.currentItem()
            if current_item and 'Network' in current_item.text(): # Updated text check
                active_view = 'suppliers'
        
        if hasattr(self.map_view, 'render_map'):
            # Pass the SERVICE_PROVIDERS instead of SUPPLIERS
            self.map_view.render_map(fleet_data, self.SERVICE_PROVIDERS, active_view)

    def refresh_ai_dashboard_visuals(self):
        """Extracts data from the model to draw the histogram and top stats."""
        raw_analytics = self.model.get_bev_regional_analytics(self.account_id)
        
        total_bevs = 0
        total_lithium = 0.0
        total_critical = 0
        regions = []
        
        # We need TWO separate arrays for the grouped histogram
        eol_0_3_counts = []
        eol_3_6_counts = []
        
        for r in raw_analytics:
            total_bevs += r['total_bevs']
            total_lithium += r['lithium_tons_at_risk']
            
            count_0_3 = r['cohorts']['0-3_months']
            count_3_6 = r['cohorts']['3-6_months']
            critical = count_0_3 + count_3_6
            total_critical += critical
            
            # Only add to graph if they have critical batteries to avoid clutter
            # Only add to graph if they have critical batteries to avoid clutter
            if critical > 0:
                raw_name = r['region_name'].split('(')[0].strip()
                
                # --- FIX: STACK THE WORDS TO PREVENT HORIZONTAL OVERLAP ---
                words = raw_name.split()
                if len(words) > 1:
                    # Turns "Northern Italy" into "Northern\nItaly"
                    short_name = f"{words[0]}\n{' '.join(words[1:])}"
                else:
                    short_name = raw_name
                # -----------------------------------------------------------
                
                regions.append(short_name)
                eol_0_3_counts.append(count_0_3)
                eol_3_6_counts.append(count_3_6)
                
        self.ai_view.populate_dashboard(total_bevs, total_lithium, total_critical, regions, eol_0_3_counts, eol_3_6_counts)

    def trigger_ai_agent(self):
        """Packages the data and streams the Gemini response to the UI."""
        payload = self.get_ai_ingestion_payload()
        self.ai_view.prepare_ai_stream()
        stream = self.agent.run_oem_battery_analysis(payload)
        self.ai_view.stream_ai_response(stream)

    def get_ai_ingestion_payload(self) -> str:
        """Structures the JSON payload with BOTH Fleet and Supplier data."""
        regional_analytics = self.model.get_bev_regional_analytics(self.account_id)
        
        payload = {
            "task": "predictive_supply_chain_analysis", 
            "global_suppliers": self.SUPPLIERS, # <--- Added Suppliers to the AI Brain!
            "regions": []
        }
        
        for r in regional_analytics:
            payload["regions"].append({
                "Region": r['region_name'],
                "Total Active BEVs": r['total_bevs'],
                "Average Fleet SoH (%)": round(r['avg_soh'], 1),
                "Critical EOL Cohorts": {
                    "0-3 Months to EOL": r['cohorts']['0-3_months'],
                    "3-6 Months to EOL": r['cohorts']['3-6_months']
                },
                "Estimated Material Yield (Tons)": round(r['lithium_tons_at_risk'], 2)
            })
 
        return json.dumps(payload, indent=4)