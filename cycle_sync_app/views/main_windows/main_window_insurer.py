from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentWindow, SubtitleLabel, FluentIcon, setTheme, Theme, NavigationItemPosition

from views.insurer_widgets.fleet_telemetry_widget import FleetTelemetryWidget
from views.insurer_widgets.oem_ai_dashboard_widget import OemAiDashboardWidget

from models.insurer_models.fleet_model import FleetModel
from controllers.db_control.insurer_controllers.fleet_controller import FleetController

class MainWindowInsurer(FluentWindow):
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None):
        super().__init__()
        setTheme(Theme.DARK)
        
        # --- FIX: Rebranded Title ---
        self.setWindowTitle("Unipol SAI - Predictive Risk Portal")
        self.resize(1100, 750)
        self.account_id = account_id

        # 1. Initialize Only the Relevant Views
        self.fleet_interface = FleetTelemetryWidget(self)
        self.supply_interface = OemAiDashboardWidget(self)
        
        # 2. Initialize Only the Relevant Models
        self.fleet_model = FleetModel()

        # 3. Initialize Controllers
        self.fleet_controller = FleetController(self.fleet_interface, self.supply_interface, self.fleet_model, self.account_id)

        self.init_navigation()

    def init_navigation(self):
        # --- FIX: Removed Blueprint Tab, kept Fleet and Analytics ---
        self.addSubInterface(self.fleet_interface, FluentIcon.GLOBE, 'Live Fleet Telemetry')
        self.addSubInterface(self.supply_interface, FluentIcon.CONNECT, 'Dynamic Risk & Premium Analytics')
        
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch to Driver',
            onClick=lambda: self.switch_role_requested.emit("DRIVER"), # Swaps back to Driver!
            position=NavigationItemPosition.BOTTOM
        )