from PyQt6.QtCore import QObject

class ActuarialController(QObject):
    def __init__(self, view, model, account_id):
        super().__init__()
        self.view = view
        self.model = model
        self.account_id = account_id

        # Wire the Ctrl+F hotkey to the math engine
        self.view.refresh_requested.connect(self.run_financial_simulation)
        
        # Load initially if data exists
        self.run_financial_simulation()

    def run_financial_simulation(self):
        """Fetches the aggregated data and pushes it to the dashboard."""
        print("[ActuarialController] Ctrl+F Detected. Calculating Financial Risk Portfolio...")
        
        dashboard_data = self.model.generate_executive_summary(self.account_id)
        # --- FIX: Fetch the new Deep Dive data ---
        deep_dive_data = self.model.get_demographic_deep_dive()
        
        if dashboard_data and deep_dive_data:
            # Pass both payloads to the view
            self.view.populate_dashboard(dashboard_data, deep_dive_data)
            print("[ActuarialController] Dashboard Successfully Updated.")
        else:
            print("[ActuarialController] No fleet data found to analyze.")

    