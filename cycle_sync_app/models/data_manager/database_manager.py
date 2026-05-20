import sqlite3
import os

# Use an absolute path to ensure we consistently hit the same database file
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cyclesync.db'))

class DatabaseManager:
    @staticmethod
    def get_connection():
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def initialize_database():
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL, role TEXT NOT NULL)''')

        # --- FIX 1: Added 'manufacturer' TEXT column ---
        cursor.execute('''CREATE TABLE IF NOT EXISTS car_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            manufacturer TEXT, 
            model_name TEXT NOT NULL UNIQUE,
            base_price REAL, manufacture_cost REAL, car_type TEXT, 
            powertrain TEXT, drivetrain TEXT, 
            owner_account_id INTEGER, image_path TEXT,
            FOREIGN KEY (owner_account_id) REFERENCES accounts(id))''')

        # --- FIX 2: Added consumer UI columns (plate, color, demographics) ---
        cursor.execute('''CREATE TABLE IF NOT EXISTS vehicles (
            vin TEXT PRIMARY KEY, model_id INTEGER, owner_id TEXT,
            production_date DATE, region_name TEXT, lat REAL, lon REAL,
            driver_age INTEGER, driver_gender TEXT, vehicle_category TEXT,
            plate_number TEXT, color TEXT,
            FOREIGN KEY (model_id) REFERENCES car_models(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS vehicle_telemetry (
            vin TEXT PRIMARY KEY, current_odometer_km INTEGER DEFAULT 0,
            driving_score INTEGER DEFAULT 100, last_sync_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vin) REFERENCES vehicles(vin))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS tire_blueprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT, model_name TEXT, 
            expected_lifespan_km INTEGER, starting_tread_depth_mm REAL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS mounted_tires (
            id INTEGER PRIMARY KEY AUTOINCREMENT, vin TEXT, blueprint_id INTEGER, position TEXT, 
            mounting_odometer_km INTEGER, current_tread_depth_mm REAL,
            FOREIGN KEY (vin) REFERENCES vehicles(vin), FOREIGN KEY (blueprint_id) REFERENCES tire_blueprints(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS global_salvage_pool (
            id INTEGER PRIMARY KEY, material_sector TEXT, component_name TEXT, 
            origin_oem TEXT, quantity_tons REAL, estimated_salvage_value_eur REAL, status TEXT)''')

        # ... (existing table creations) ...
        cursor.execute('''CREATE TABLE IF NOT EXISTS global_salvage_pool (
            id INTEGER PRIMARY KEY, material_sector TEXT, component_name TEXT, 
            origin_oem TEXT, quantity_tons REAL, estimated_salvage_value_eur REAL, status TEXT)''')

        # 🆕 ADD THIS: The granular components table for the Driver App
        cursor.execute('''CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_vin TEXT,
            category TEXT,
            position TEXT,
            wear_percent REAL,
            status TEXT,
            FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin))''')

        # 🆕 ADD THIS: Ensure at least one Tire Blueprint exists for the FK constraint
        cursor.execute("SELECT COUNT(*) FROM tire_blueprints")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO tire_blueprints (brand, model_name, expected_lifespan_km, starting_tread_depth_mm) 
                VALUES ('Pirelli', 'P Zero Elettro', 45000, 8.0)
            """)

        conn.commit()
        DatabaseManager.inject_core_dummy_data(conn)
        DatabaseManager.seed_base_car_models(conn) # <-- FIX 3: Seed cars before simulation
        DatabaseManager.inject_macro_market_data(conn)
        conn.close()

    @staticmethod
    def inject_core_dummy_data(conn):
        cursor = conn.cursor()
        
        dummy_accounts = [('mario_driver', 'hash', 'DRIVER'), ('maserati_oem', 'hash', 'OEM'), ('eco_recycler', 'hash', 'RECYCLER')]
        for user, pwd, role in dummy_accounts:
            try:
                cursor.execute('INSERT INTO accounts (username, password_hash, role) VALUES (?, ?, ?)', (user, pwd, role))
            except sqlite3.IntegrityError:
                pass
        conn.commit()

    @staticmethod
    def seed_base_car_models(conn):
        """Seeds the required car models so the simulation has data to work with."""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM car_models")
        if cursor.fetchone()[0] == 0:
            print("🌱 Seeding base car models into cyclesync.db...")
            models = [
                # Manufacturer, Model, Type, Powertrain, Price
                ('Maserati', 'Grecale Folgore', 'SUV', 'BEV', 120000.0), # Essential for the demo
                ('Tesla', 'Model 3', 'Sedan', 'BEV', 45000.0),
                ('Fiat', '500e', 'Hatchback', 'BEV', 30000.0),
                ('Volkswagen', 'Golf', 'Hatchback', 'ICE', 28000.0),
                ('BMW', 'X5', 'SUV', 'ICE', 75000.0),
                ('Toyota', 'Yaris', 'Utilitarian', 'Hybrid', 22000.0)
            ]
            
            # Using INSERT OR IGNORE protects against crashes if data already exists
            cursor.executemany("""
                INSERT OR IGNORE INTO car_models (manufacturer, model_name, car_type, powertrain, base_price) 
                VALUES (?, ?, ?, ?, ?)
            """, models)
            conn.commit()

    @staticmethod
    def inject_macro_market_data(conn):
        # We now calculate this dynamically via MacroMarketModel, no static injection needed.
        pass