import sqlite3
from models.data_manager.database_manager import DatabaseManager

class OEMModel:
    def __init__(self):
        DatabaseManager.initialize_database()

    # Add 'owner_username' to the parameters
    def create_car_model(self, model_name: str, car_type: str, powertrain: str, drivetrain: str, account_id: int, owner_username: str, plate_number: str, image_path: str = ""):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # 1. Defensively add the plate number column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE vehicles ADD COLUMN plate_number TEXT DEFAULT 'UNKNOWN'")
            conn.commit()
        except sqlite3.OperationalError:
            pass # Column already exists
            
        try:
            # 2. Hardcode the old price constraints to 0.0 so the DB schema doesn't crash
            cursor.execute('''
                INSERT INTO car_models (model_name, base_price, manufacture_cost, car_type, powertrain, drivetrain, owner_account_id, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (model_name, 0.0, 0.0, car_type, powertrain, drivetrain, account_id, image_path))
            
            model_id = cursor.lastrowid
            import uuid
            import datetime
            
            vin = f"ZAM{str(model_name)[:4].upper()}{str(uuid.uuid4().hex)[:6].upper()}"
            today = datetime.date.today().strftime('%Y-%m-%d')
            
            # 3. Insert the new car with the Plate Number
            cursor.execute("INSERT INTO vehicles (vin, model_id, owner_id, production_date, region_name, plate_number) VALUES (?, ?, ?, ?, ?, ?)", (vin, model_id, owner_username, today, 'Unipol-Registered', plate_number))
            cursor.execute("INSERT INTO vehicle_telemetry (vin, current_odometer_km, driving_score) VALUES (?, ?, ?)", (vin, 0, 100))
            
            conn.commit()
            
            from models.driver_models.tire_model import TireModel
            tm = TireModel()
            tm.initialize_vehicle_tires(vin)
            
            return vin # <--- FIX: Return the VIN instead of True!
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_models_by_account(self, account_id: int):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        # NOTE: The index of the columns returned here is important for the View!
        cursor.execute('''
            SELECT id, model_name, base_price, manufacture_cost, 
                   car_type, powertrain, drivetrain, image_path 
            FROM car_models
            WHERE owner_account_id = ?
        ''', (account_id,))
        results = cursor.fetchall()
        conn.close()
        return results