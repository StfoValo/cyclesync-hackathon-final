from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (FluentWindow, SubtitleLabel, FluentIcon, 
                            setTheme, Theme, NavigationItemPosition, ComboBox)

from views.Driver_widgets.garage_widget import GarageWidget
from views.Driver_widgets.tire_tracker_widget import TireTrackerWidget
from views.Driver_widgets.powertrain_widgets.powertrain_hub_widget import PowertrainHubWidget

# --- NEW: Import the Eco Coach ---
from views.Driver_widgets.eco_coach_widget import EcoCoachWidget
from controllers.db_control.driver_controllers.eco_coach_controller import EcoCoachController

from models.driver_models.vehicle_model import VehicleModel
from models.driver_models.tire_model import TireModel
from models.insurer_models.oem_model import OEMModel 

from controllers.db_control.driver_controllers.garage_controller import GarageController
from controllers.db_control.driver_controllers.tire_controller import TireController
from controllers.db_control.driver_controllers.powertrain_hub_controller import PowertrainHubController

class PlaceholderPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(" ", "").replace("&", ""))
        self.label = SubtitleLabel(text, self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)

class MainWindowUser(FluentWindow):
    switch_role_requested = pyqtSignal(str)

    def __init__(self, account_id=None, username=None):
        super().__init__()
        self.account_id = account_id
        self.username = username
        
        setTheme(Theme.DARK)
        self.setWindowTitle("CycleSync - Driver Dashboard")
        self.resize(1000, 700)

        # Models
        self.vehicle_model = VehicleModel()
        self.tire_model = TireModel()
        self.oem_model = OEMModel() 
        
        # 1. Garage Setup
        self.garage_widget = GarageWidget()
        self.garage_controller = GarageController(self.garage_widget, self.vehicle_model, self.oem_model, self.username, self.account_id)
        
        # Global Vehicle Selector
        self.vehicle_combo = ComboBox(self)
        self.vehicle_combo.setMinimumWidth(250)
        self.vehicle_combo.currentIndexChanged.connect(self._on_global_vehicle_changed)
        self.titleBar.layout().insertWidget(1, self.vehicle_combo)
        self.titleBar.layout().insertSpacing(2, 20)
        
        # 2. Eco-Coach Setup (NEW)
        self.eco_coach_interface = EcoCoachWidget()
        self.eco_coach_controller = EcoCoachController(self.eco_coach_interface, self.vehicle_model, self.username)

        # 3. Powertrain & Tires Setup
        self.powertrain_interface = PowertrainHubWidget()
        self.powertrain_controller = PowertrainHubController(self.powertrain_interface, self.vehicle_model, self.username)
        
        self.tire_interface = TireTrackerWidget() 
        self.tire_controller = TireController(self.tire_interface, self.tire_model, self.vehicle_model, self.username)

        self.privacy_interface = PlaceholderPage("Data Privacy & Consent")
        
        # --- LIVE REFRESH SIGNALS ---
        # When a trip is simulated in the Garage, instantly refresh the other tabs!
        self.garage_widget.trip_simulated.connect(lambda v: self.eco_coach_controller.load_eco_data())
        self.garage_widget.trip_simulated.connect(lambda v: self.powertrain_controller.set_active_vin(v))
        self.garage_widget.trip_simulated.connect(lambda v: self.tire_controller.set_active_vin(v))
        self.garage_widget.vehicle_added.connect(self._on_vehicle_added)

        self.init_navigation()
        self.load_global_vehicles()
        
    def _on_vehicle_added(self, new_vin):
        """Re-fetches the database and snaps the UI to the newly registered car."""
        self.load_global_vehicles()
        
        # Find the index of the newly added VIN and select it
        index = self.vehicle_combo.findData(new_vin)
        if index >= 0:
            self.vehicle_combo.setCurrentIndex(index)
            
    def load_global_vehicles(self):
        vehicles = self.vehicle_model.get_vehicles_by_owner(self.username)
        self.vehicle_combo.blockSignals(True)
        self.vehicle_combo.clear()
        for v in vehicles:
            vin, model_name = v[0], v[1]
            self.vehicle_combo.addItem(f"{model_name} ({vin[-6:]})", userData=vin)
        self.vehicle_combo.blockSignals(False)
        
        if vehicles:
            self._on_global_vehicle_changed()
        else:
            self._clear_all_vins()

    def _clear_all_vins(self):
        self.garage_controller.set_active_vin(None)
        self.eco_coach_controller.set_active_vin(None)
        self.powertrain_controller.set_active_vin(None)
        self.tire_controller.set_active_vin(None)

    def _on_global_vehicle_changed(self):
        vin = self.vehicle_combo.currentData()
        if vin:
            self.garage_controller.set_active_vin(vin)
            self.eco_coach_controller.set_active_vin(vin) # Connect Eco Coach
            self.powertrain_controller.set_active_vin(vin)
            self.tire_controller.set_active_vin(vin)

    def init_navigation(self):
        self.addSubInterface(self.garage_widget, FluentIcon.HEART, 'My Garage')
        
        # Add the new tab right after Garage!
        self.addSubInterface(self.eco_coach_interface, FluentIcon.LEAF, 'Eco-Coach Insights') 
        
        self.addSubInterface(self.powertrain_interface, FluentIcon.POWER_BUTTON, 'Powertrain Diagnostics')
        self.addSubInterface(self.tire_interface, FluentIcon.SYNC, 'Tire Lifecycle Tracker')
        self.addSubInterface(self.privacy_interface, FluentIcon.FINGERPRINT, 'Data Privacy & Consent')
        
        self.navigationInterface.addItem(
            routeKey='JudgeSwitch',
            icon=FluentIcon.PEOPLE,
            text='Judge Mode: Switch Role',
            onClick=lambda: self.switch_role_requested.emit("OEM"),
            position=NavigationItemPosition.BOTTOM
        )