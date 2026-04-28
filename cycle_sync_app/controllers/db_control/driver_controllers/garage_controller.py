import os
import shutil
from PyQt6.QtCore import QObject, Qt
from qfluentwidgets import InfoBar, InfoBarPosition

# --- BULLETPROOF PATH RESOLUTION ---
# 1. Force the file path to be absolute (e.g., C:/.../driver_controllers)
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

# 2. Walk exactly 3 steps back up the tree to reach the cycle_sync_app root
DB_CONTROL_DIR = os.path.dirname(CURRENT_DIR)
CONTROLLERS_DIR = os.path.dirname(DB_CONTROL_DIR)
APP_DIR = os.path.dirname(CONTROLLERS_DIR)

# 3. Lock in the storage directory
STORAGE_DIR = os.path.join(APP_DIR, 'storage', 'car_photos')

class GarageController(QObject):
    # Added oem_model and account_id to __init__
    def __init__(self, view, vehicle_model, oem_model, username, account_id):
        super().__init__()
        self.view = view
        self.vehicle_model = vehicle_model
        self.oem_model = oem_model # The engine to mint cars!
        self.username = username
        self.account_id = account_id
        
        self.current_vin = None
        
        # Wire the old UI to the new UI
        self.view.btn_add_car.clicked.connect(self.show_registration_form)
        self.view.form_page.cancel_requested.connect(self.show_garage)
        self.view.form_page.form_submitted.connect(self.handle_vehicle_registration)
        self.view.trip_simulated.connect(self.handle_trip_simulation)

    def show_registration_form(self):
        self.view.stacked_widget.setCurrentIndex(1)
        
    def show_garage(self):
        self.view.form_page.model_name_input.clear()
        self.view.stacked_widget.setCurrentIndex(0)

    def handle_vehicle_registration(self, data):
        """Uses the OEM Model to mint a new car for the driver."""
        print("\n" + "="*50)
        print("[UPLOAD DIAGNOSTICS] Starting Vehicle Registration")
        
        model_name = data['model_name']
        plate_number = data['plate_number']
        car_type = data['car_type']
        powertrain = data['powertrain']
        drivetrain = data['drivetrain']
        original_image_path = data['image_path']
        
        print(f"[UPLOAD DIAGNOSTICS] Original selected image path: '{original_image_path}'")
        print(f"[UPLOAD DIAGNOSTICS] Calculated Target Directory: '{STORAGE_DIR}'")
        
        stored_relative_path = ""
        
        # 1. Check if the image was actually provided by the UI
        if original_image_path:
            # 2. Check if Python can actually read the file on your hard drive
            if os.path.exists(original_image_path):
                print("[UPLOAD DIAGNOSTICS] ✅ Original image exists on disk. Attempting copy...")
                
                # Force create the directory if it's missing
                os.makedirs(STORAGE_DIR, exist_ok=True)
                print(f"[UPLOAD DIAGNOSTICS] Directory ensured at: '{STORAGE_DIR}'")
                
                safe_model_name = model_name.replace(" ", "_").lower()
                file_extension = os.path.splitext(original_image_path)[1]
                new_filename = f"{safe_model_name}{file_extension}"
                destination_absolute_path = os.path.join(STORAGE_DIR, new_filename)
                
                print(f"[UPLOAD DIAGNOSTICS] Copying to: '{destination_absolute_path}'")
                
                try:
                    if os.path.abspath(original_image_path) != os.path.abspath(destination_absolute_path):
                        shutil.copy2(original_image_path, destination_absolute_path)
                    print("[UPLOAD DIAGNOSTICS] ✅ File successfully copied to storage!")
                    stored_relative_path = os.path.join('storage', 'car_photos', new_filename).replace('\\', '/')
                except Exception as e:
                    print(f"[UPLOAD DIAGNOSTICS] ❌ COPY FAILED with error: {e}")
            else:
                print(f"[UPLOAD DIAGNOSTICS] ❌ Python cannot find the original image! Path does not exist: {original_image_path}")
        else:
            print("[UPLOAD DIAGNOSTICS] ⚠️ No image was selected in the form.")
            
        print("="*50 + "\n")
            
        # Call the updated model
        new_vin = self.oem_model.create_car_model(
            model_name=model_name, car_type=car_type, powertrain=powertrain, drivetrain=drivetrain,
            account_id=self.account_id, owner_username=self.username, plate_number=plate_number, image_path=stored_relative_path
        )
        
        if new_vin:
            InfoBar.success(title='Registration Complete', content=f'UnipolMove initialized for Plate: {plate_number}.', orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.view)
            self.view.vehicle_added.emit(new_vin) 
            self.show_garage()
        else:
            InfoBar.error(title='Error', content='Could not register vehicle.', orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=3000, parent=self.view)
        
    def set_active_vin(self, vin):
        self.active_vin = vin
        self.load_garage_data()
        
    def handle_trip_simulation(self, vin):
        TripSimulator.simulate_trip(vin)
        self.load_garage_data()
        
    def load_garage_data(self):
        self.view.clear_cards()
        if not self.active_vin:
            self.view.show_empty_message()
            return
            
        vehicles = self.vehicle_model.get_vehicles_by_owner(self.username)
        for row in vehicles:
            if row[0] == self.active_vin:
                # Safely unpack just the first 6 elements for the UI card
                vin_str, model_name, car_type, image_path, odometer, driving_score = row[:6]
                
                absolute_image_path = ""
                if image_path:
                    if not os.path.isabs(image_path):
                        absolute_image_path = os.path.join(APP_DIR, image_path)
                    else:
                        absolute_image_path = image_path
                
                self.view.render_vehicle_card(vin_str, model_name, car_type, absolute_image_path, odometer, driving_score)
                break