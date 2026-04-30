from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentWindow, SubtitleLabel, FluentIcon, setTheme, Theme, NavigationItemPosition

from views.insurer_widgets.fleet_telemetry_widget import FleetTelemetryWidget
from views.insurer_widgets.actuarial_dashboard_widget import ActuarialDashboardWidget
from views.insurer_widgets.oem_ai_dashboard_widget import OemAiDashboardWidget
from views.insurer_widgets.ai_strategy_widget import AiStrategyWidget

from models.insurer_models.fleet_model import FleetModel
from models.insurer_models.actuarial_model import ActuarialModel

from controllers.db_control.insurer_controllers.fleet_controller import FleetController
from controllers.db_control.insurer_controllers.actuarial_controller import ActuarialController

class MainWindowInsurer(FluentWindow):
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None):
        super().__init__()
        setTheme(Theme.DARK)
        
        self.setWindowTitle("Predictive Risk & Actuarial Portal")
        self.resize(1200, 800)
        self.account_id = account_id

        # 1. Initialize Views (All 4 Tabs!)
        self.fleet_interface = FleetTelemetryWidget(self)
        self.actuarial_interface = ActuarialDashboardWidget(self)
        self.vsi_interface = OemAiDashboardWidget(self)
        self.strategy_interface = AiStrategyWidget(self)
        
        # 2. Initialize Models
        self.fleet_model = FleetModel()
        self.actuarial_model = ActuarialModel()

        # 3. Initialize Controllers with STRICT mapping
        self.actuarial_controller = ActuarialController(self.actuarial_interface, self.actuarial_model, self.account_id)
        
        # Notice we pass `self.vsi_interface` as the second argument here, NOT the actuarial interface!
        self.fleet_controller = FleetController(self.fleet_interface, self.vsi_interface, self.strategy_interface, self.fleet_model, self.account_id)

        self.init_navigation()

    def init_navigation(self):
        self.addSubInterface(self.fleet_interface, FluentIcon.GLOBE, 'Live Fleet Telemetry')
        self.addSubInterface(self.actuarial_interface, FluentIcon.PIE_SINGLE, 'Executive Risk Summary')
        self.addSubInterface(self.vsi_interface, FluentIcon.HEART, 'Predictive Asset Risk (VSI)')
        self.addSubInterface(self.strategy_interface, FluentIcon.ROBOT, 'AI Routing Directive')
        
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch to Driver',
            onClick=lambda: self.switch_role_requested.emit("DRIVER"), 
            position=NavigationItemPosition.BOTTOM
        )