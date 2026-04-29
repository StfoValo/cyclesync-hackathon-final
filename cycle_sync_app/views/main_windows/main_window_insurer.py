from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentWindow, SubtitleLabel, FluentIcon, setTheme, Theme, NavigationItemPosition

from views.insurer_widgets.fleet_telemetry_widget import FleetTelemetryWidget
from views.insurer_widgets.actuarial_dashboard_widget import ActuarialDashboardWidget # NEW!
from views.insurer_widgets.oem_ai_dashboard_widget import OemAiDashboardWidget

from models.insurer_models.fleet_model import FleetModel
from models.insurer_models.actuarial_model import ActuarialModel # NEW!

from controllers.db_control.insurer_controllers.fleet_controller import FleetController
from controllers.db_control.insurer_controllers.actuarial_controller import ActuarialController # NEW!

class MainWindowInsurer(FluentWindow):
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None):
        super().__init__()
        setTheme(Theme.DARK)
        
        # --- FIX: Generic White-Label Title ---
        self.setWindowTitle("Predictive Risk & Actuarial Portal")
        self.resize(1150, 800)
        self.account_id = account_id

        # 1. Initialize Views (3 Tabs)
        self.fleet_interface = FleetTelemetryWidget(self)
        self.actuarial_interface = ActuarialDashboardWidget(self) # NEW!
        self.ai_interface = OemAiDashboardWidget(self)
        
        # 2. Initialize Models
        self.fleet_model = FleetModel()
        self.actuarial_model = ActuarialModel() # NEW!

        # 3. Initialize Controllers
        self.fleet_controller = FleetController(self.fleet_interface, self.ai_interface, self.fleet_model, self.account_id)
        self.actuarial_controller = ActuarialController(self.actuarial_interface, self.actuarial_model, self.account_id) # NEW!

        self.init_navigation()

    def init_navigation(self):
        # Add the 3 tabs in logical order
        self.addSubInterface(self.fleet_interface, FluentIcon.GLOBE, 'Live Fleet Telemetry')
        self.addSubInterface(self.actuarial_interface, FluentIcon.PIE_SINGLE, 'Executive Risk Summary') # NEW!
        self.addSubInterface(self.ai_interface, FluentIcon.ROBOT, 'AI Strategy Directive')
        
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch to Driver',
            onClick=lambda: self.switch_role_requested.emit("DRIVER"), 
            position=NavigationItemPosition.BOTTOM
        )