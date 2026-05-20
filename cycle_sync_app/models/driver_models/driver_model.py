import sqlite3
import random
from models.data_manager.database_manager import DatabaseManager

class DriverModel:
    def __init__(self):
        self._ensure_driver_tables()
        self._ensure_missing_enterprise_columns()

    def _ensure_driver_tables(self):
        """Creates the necessary tables for the driver app."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS driver_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            phone TEXT,
            pinned_vin TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS driver_vehicles (
            driver_id INTEGER NOT NULL,
            vin TEXT NOT NULL,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (driver_id, vin),
            FOREIGN KEY (driver_id) REFERENCES driver_accounts(id),
            FOREIGN KEY (vin) REFERENCES vehicles(vin)
        )
        """)
        
        conn.commit()
        conn.close()

    def _ensure_missing_enterprise_columns(self):
        """
        Dynamically patches the enterprise tables to include consumer data 
        (color, plates, manufacturer) if they don't already exist.
        """
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        # Add to vehicles
        for col, ctype in [("plate_number", "TEXT"), ("color", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE vehicles ADD COLUMN {col} {ctype}")
            except sqlite3.OperationalError:
                pass # Column already exists

        # Add to car_models
        for col, ctype in [("manufacturer", "TEXT"), ("powertrain", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE car_models ADD COLUMN {col} {ctype}")
            except sqlite3.OperationalError:
                pass 

        conn.commit()
        conn.close()

    def seed_demo_driver(self):
        """Seeds Andrea and injects pristine demo data for the investor presentation."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # ==========================================
        # 🆕 THE PERMANENT FIX: THE "GHOST CAR" PREVENTER
        # Always wipe Andrea's old link before assigning a new car.
        # This means you NEVER have to manually delete the DB again!
        # ==========================================
        cursor.execute("DELETE FROM driver_vehicles WHERE driver_id = 1")
        cursor.execute("DELETE FROM driver_accounts WHERE id = 1")
        
        # Grab a high-end vehicle that was just simulated
        cursor.execute("""
            SELECT vin, model_id FROM vehicles 
            WHERE vehicle_category IN ('SUV', 'Sportscar') 
            LIMIT 1
        """)
        demo_vin_row = cursor.fetchone()
        
        # Fallback
        if not demo_vin_row:
            cursor.execute("SELECT vin, model_id FROM vehicles LIMIT 1")
            demo_vin_row = cursor.fetchone()

        if demo_vin_row:
            demo_vin = demo_vin_row[0]
            model_id = demo_vin_row[1]
            
            # 1. Insert Andrea
            cursor.execute("""
            INSERT INTO driver_accounts (id, email, display_name, phone, pinned_vin) 
            VALUES (1, 'andrea.moretti@email.it', 'Andrea', '+39 333 1234567', ?)
            """, (demo_vin,))
            
            # 2. Link Vehicle to Garage
            cursor.execute("""
            INSERT INTO driver_vehicles (driver_id, vin) 
            VALUES (1, ?)
            """, (demo_vin,))

            # 3. 🎩 THE MAGIC TRICK: Update the existing Maserati model instead of inserting
            cursor.execute("""
                UPDATE vehicles 
                SET plate_number = 'FW829AB', color = 'Blu Notte' 
                WHERE vin = ?
            """, (demo_vin,))

            # Find the ID of the Maserati we seeded in DatabaseManager
            cursor.execute("SELECT id FROM car_models WHERE model_name = 'Grecale Folgore'")
            existing_model = cursor.fetchone()
            model_id_to_update = existing_model[0] if existing_model else model_id

            # Link grabbed vehicle to Maserati model
            if existing_model:
                cursor.execute("UPDATE vehicles SET model_id = ? WHERE vin = ?", (existing_model[0], demo_vin))

            cursor.execute("""
                UPDATE car_models 
                SET manufacturer = 'Maserati', powertrain = 'BEV' 
                WHERE id = ?
            """, (model_id_to_update,))
                
            # ==========================================
            # 4. SEED GRANULAR COMPONENTS FOR NEW UI
            # ==========================================
            cursor.execute("DELETE FROM mounted_tires WHERE vin = ?", (demo_vin,))
            cursor.execute("DELETE FROM components WHERE vehicle_vin = ?", (demo_vin,))

            # Seed 4 individual tires (Rear Right is worn out to trigger the warning)
            tires = [
                (demo_vin, 1, 'FL', 0, 6.2), # Front Left (Good)
                (demo_vin, 1, 'FR', 0, 6.1), # Front Right (Good)
                (demo_vin, 1, 'RL', 0, 5.8), # Rear Left (Good)
                (demo_vin, 1, 'RR', 0, 2.1)  # Rear Right (Warning)
            ]
            cursor.executemany("""
                INSERT INTO mounted_tires 
                (vin, blueprint_id, position, mounting_odometer_km, current_tread_depth_mm) 
                VALUES (?, ?, ?, ?, ?)
            """, tires)

            # Seed granular brakes and battery
            components = [
                (demo_vin, 'brake_pad', 'front', 34.7, 'installed'), # 34.7% wear (Good)
                (demo_vin, 'brake_pad', 'rear', 84.0, 'installed'),  # 84.0% wear (Warning)
                (demo_vin, 'ev_battery', 'main', 4.5, 'installed')   # 4.5% degradation (Good)
            ]
            cursor.executemany("""
                INSERT INTO components (vehicle_vin, category, position, wear_percent, status)
                VALUES (?, ?, ?, ?, ?)
            """, components)
            
            conn.commit()
            print(f"✅ Demo driver seeded! Pinned VIN: {demo_vin} (Maserati Grecale Folgore)")
            success = True
        else:
            print("⚠️ Warning: No vehicles found to link to the demo driver.")
            success = False
            
        conn.close()
        return success