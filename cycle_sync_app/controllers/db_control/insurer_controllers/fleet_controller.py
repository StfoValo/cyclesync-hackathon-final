import json
from PyQt6.QtCore import QObject
from models.insurer_models.actuarial_model import ActuarialModel # <--- NEW IMPORT
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

    def __init__(self, map_view, ai_dashboard_view, strategy_view, model, account_id):
        super().__init__()
        self.map_view = map_view            
        self.ai_view = ai_dashboard_view
        self.strategy_view = strategy_view  # <--- FIX: Added the 3rd UI view!
        self.model = model
        self.account_id = account_id
        
        # Instantiate the models
        self.actuarial_model = ActuarialModel()
        self.agent = AIOrchestrator()
        
        # Connect Map Signals
        self.map_view.simulate_requested.connect(self.run_simulation)
        self.map_view.view_toggle.currentItemChanged.connect(self.load_fleet_data)
        
        # --- FIX: Wire the 'Generate' button from the new AI Tab! ---
        if hasattr(self.strategy_view, 'analyze_requested'):
            self.strategy_view.analyze_requested.connect(self.trigger_ai_agent)
        
        self.load_fleet_data()
        self.refresh_ai_dashboard_visuals()

    def run_simulation(self):
        """Triggers the Monte Carlo simulation and refreshes both UIs."""
        self.model.simulate_regional_fleet(self.account_id)
        self.load_fleet_data()
        self.refresh_ai_dashboard_visuals()

    def load_fleet_data(self, *args):
        """Passes both the fleet data and the supplier data to the map."""
        fleet_data = self.model.get_regional_kpis(self.account_id)
        
        active_view = 'fleet' 
        if args and isinstance(args[0], str):
            active_view = args[0]
        else:
            current_item = self.map_view.view_toggle.currentItem()
            if current_item and 'Network' in current_item.text(): 
                active_view = 'suppliers'
        
        if hasattr(self.map_view, 'render_map'):
            self.map_view.render_map(fleet_data, self.SERVICE_PROVIDERS, active_view)

    def refresh_ai_dashboard_visuals(self):
        """Fetches the VSI Component data and pushes it to the Asset Risk Dashboard."""
        # --- FIX: Replaced old battery fetching with the new VSI Portfolio ---
        portfolio_data = self.actuarial_model.get_asset_risk_portfolio()
        
        if hasattr(self.ai_view, 'populate_dashboard'):
            self.ai_view.populate_dashboard(portfolio_data)

    # Note: We can safely leave these AI methods here as stubs for when we rebuild 
    # the AI Agent functionality in Tab 3 of your master plan!
    def trigger_ai_agent(self):
        pass

    def get_ai_ingestion_payload(self) -> str:
        return "{}"

    def trigger_ai_agent(self, selected_region: str):
        """
        Triggered by the UI when the Actuary clicks 'Analyze Region'.
        Packages local data and streams the Gemini response back to the UI.
        """
        payload = self.get_ai_ingestion_payload(selected_region)
        
        # --- FIX: Send the stream to the strategy_view (The new AI Terminal), NOT the ai_view ---
        if hasattr(self.strategy_view, 'prepare_ai_stream'):
            self.strategy_view.prepare_ai_stream(selected_region)
            
        stream = self.agent.run_actuarial_strategy_analysis(payload)
        
        if hasattr(self.strategy_view, 'stream_ai_response'):
            self.strategy_view.stream_ai_response(stream)

    def get_ai_ingestion_payload(self, target_region: str) -> str:
        """
        Extracts ONLY the VSI data and Unipol partners for the selected region 
        to ensure hyper-local, accurate AI orchestration.
        """
        # 1. Fetch the full national portfolio
        portfolio_data = self.actuarial_model.get_asset_risk_portfolio()
        
        # 2. Extract ONLY the target region's physics data
        region_stats = next((r for r in portfolio_data['regional'] if r['region'] == target_region), None)
        
        if not region_stats:
            return json.dumps({"error": f"No telemetry data found for region: {target_region}"})
            
        # 3. Extract ONLY the Unipol repair network located in this specific region
        local_network = [sp for sp in self.SERVICE_PROVIDERS if sp['region'] == target_region]
        
        # 4. Construct the highly-optimized LLM JSON Payload
        payload = {
            "Analysis_Target": target_region,
            "Regional_Asset_Risk": {
                "Overall_VSI": {
                    "Safe": region_stats['vsi'][0],
                    "Warning": region_stats['vsi'][1],
                    "Critical_Failure_Risk": region_stats['vsi'][2]
                },
                "Braking_Systems": {
                    "Critical_Need_Replacement (<3mm)": region_stats['brakes'][2]
                },
                "Tire_Wear": {
                    "Critical_Blowout_Risk (<2mm)": region_stats['tires'][2]
                }
            },
            "Available_Local_Network": local_network
        }
        
        return json.dumps(payload, indent=2)