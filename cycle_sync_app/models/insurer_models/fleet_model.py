import sqlite3
import random
import uuid
from datetime import datetime, timedelta
from models.data_manager.database_manager import DatabaseManager
from models.driver_models.powertrain_models.bev_model import BEVModel

class FleetModel:
    # 1 Simulated Row = 2,500 Real Cars (Keeps the app blazing fast!)
    SCALE_FACTOR = 2500 
    
    # --- EXCLUSIVE ITALIAN REGIONS (Actual Unipol Market Size - 22%) ---
    REGIONS = [
        {"name": "Lombardia", "lat": 45.4642, "lon": 9.1900, "coeff": 1386000},
        {"name": "Lazio", "lat": 41.9028, "lon": 12.4964, "coeff": 858000},
        {"name": "Campania", "lat": 40.8518, "lon": 14.2681, "coeff": 770000},
        {"name": "Sicilia", "lat": 38.1157, "lon": 13.3615, "coeff": 759000},
        {"name": "Veneto", "lat": 45.4408, "lon": 12.3155, "coeff": 715000},
        {"name": "Emilia-Romagna", "lat": 44.4949, "lon": 11.3426, "coeff": 660000},
        {"name": "Piemonte", "lat": 45.0703, "lon": 7.6868, "coeff": 649000},
        {"name": "Puglia", "lat": 41.1171, "lon": 16.8719, "coeff": 550000},
        {"name": "Toscana", "lat": 43.7696, "lon": 11.2558, "coeff": 539000},
        {"name": "Calabria", "lat": 38.9059, "lon": 16.5944, "coeff": 286000},
        {"name": "Sardegna", "lat": 39.2238, "lon": 9.1217, "coeff": 242000},
        {"name": "Marche", "lat": 43.6158, "lon": 13.5189, "coeff": 231000},
        {"name": "Trentino-Alto Adige", "lat": 46.0679, "lon": 11.1211, "coeff": 220000},
        {"name": "Liguria", "lat": 44.4056, "lon": 8.9463, "coeff": 198000},
        {"name": "Abruzzo", "lat": 42.3498, "lon": 13.3995, "coeff": 198000},
        {"name": "Friuli-Venezia Giulia", "lat": 45.6495, "lon": 13.7768, "coeff": 187000},
        {"name": "Umbria", "lat": 43.1107, "lon": 12.3908, "coeff": 143000},
        {"name": "Basilicata", "lat": 40.6333, "lon": 15.8000, "coeff": 88000},
        {"name": "Molise", "lat": 41.5603, "lon": 14.6599, "coeff": 48400},
        {"name": "Valle d'Aosta", "lat": 45.7373, "lon": 7.3201, "coeff": 39600}
    ]

    def __init__(self):
        self._ensure_region_columns()

    def _ensure_region_columns(self):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE vehicles ADD COLUMN region_name TEXT")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN lat REAL")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN lon REAL")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        conn.close()

    def simulate_regional_fleet(self, account_id: int):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM car_models")
        model_rows = cursor.fetchall()
        if not model_rows:
            conn.close()
            return False 

        cursor.execute("DELETE FROM vehicle_telemetry WHERE vin IN (SELECT vin FROM vehicles WHERE owner_id = 'SIMULATED')")
        cursor.execute("DELETE FROM vehicles WHERE owner_id = 'SIMULATED'")

        vehicles_data = []
        telemetry_data = []

        for region in self.REGIONS:
            # Safely scale down the generation to prevent DB freezing
            num_cars_per_model = max(1, int((region["coeff"] / self.SCALE_FACTOR) / 3))
            
            for _ in range(3): 
                model_id = random.choice(model_rows)[0]
                
                for _ in range(num_cars_per_model):
                    vin = f"SIM{uuid.uuid4().hex[:14].upper()}"
                    days_old = random.randint(30, 3650)
                    prod_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')
                    
                    lat_jitter = region["lat"] + random.uniform(-0.4, 0.4)
                    lon_jitter = region["lon"] + random.uniform(-0.4, 0.4)

                    vehicles_data.append((vin, model_id, 'SIMULATED', prod_date, region["name"], lat_jitter, lon_jitter))
                    odo = int(days_old * random.uniform(30, 60)) 
                    score = random.randint(40, 100) 
                    telemetry_data.append((vin, odo, score))

        cursor.executemany("INSERT INTO vehicles (vin, model_id, owner_id, production_date, region_name, lat, lon) VALUES (?, ?, ?, ?, ?, ?, ?)", vehicles_data)
        cursor.executemany("INSERT INTO vehicle_telemetry (vin, current_odometer_km, driving_score) VALUES (?, ?, ?)", telemetry_data)
        
        conn.commit()
        conn.close()
        return True

    def get_regional_kpis(self, account_id: int):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # --- FIX: Multiply the results by the Scale Factor so the UI shows Millions! ---
        cursor.execute(f'''
            SELECT v.region_name, 
                   COUNT(v.vin) * {self.SCALE_FACTOR} as total_cars,
                   AVG(t.current_odometer_km) as avg_km,
                   AVG(v.lat) as center_lat,
                   AVG(v.lon) as center_lon,
                   SUM(CASE WHEN t.driving_score < 60 THEN 1 ELSE 0 END) * {self.SCALE_FACTOR} as risk_high,
                   SUM(CASE WHEN t.driving_score >= 60 AND t.driving_score < 85 THEN 1 ELSE 0 END) * {self.SCALE_FACTOR} as risk_moderate,
                   SUM(CASE WHEN t.driving_score >= 85 THEN 1 ELSE 0 END) * {self.SCALE_FACTOR} as risk_safe
            FROM vehicles v
            JOIN car_models c ON v.model_id = c.id
            JOIN vehicle_telemetry t ON v.vin = t.vin
            WHERE v.region_name IS NOT NULL
            GROUP BY v.region_name
        ''')
        
        columns = [column[0] for column in cursor.description]
        raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return raw_results

    def get_bev_regional_analytics(self, account_id: int):
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.region_name, c.model_name, c.car_type, c.base_price,
                   t.current_odometer_km, t.driving_score, v.production_date
            FROM vehicles v
            JOIN car_models c ON v.model_id = c.id
            JOIN vehicle_telemetry t ON v.vin = t.vin
            WHERE c.powertrain = 'BEV' AND v.region_name IS NOT NULL
        ''')
        bev_data = cursor.fetchall()
        conn.close()

        bev_model = BEVModel()
        regions = {}
        from datetime import datetime
        today = datetime.today()

        for row in bev_data:
            region, model_name, car_type, price, odo, score, prod_date = row

            try:
                p_date = datetime.strptime(prod_date, "%Y-%m-%d")
                age_yr = max((today - p_date).days / 365.25, 0.1)
            except ValueError:
                age_yr = 2.0

            params = {
                'chem': 'NMC' if 'SUV' in car_type.upper() else 'LFP',
                'cap_kWh': 100.0 if 'SUV' in car_type.upper() else 60.0,
                'wltp_km': 600.0 if 'SUV' in car_type.upper() else 400.0,
                'age_yr': age_yr,
                'km_total': odo,
                'veh_price': price,
                'temp_C': 15.0,
                'driving_score': score
            }

            kpis = bev_model.estimate_battery_life(params)
            soh = kpis['soh']

            total_loss = 100.0 - soh
            annual_loss_rate = total_loss / max(age_yr, 0.1)
            
            years_to_eol = max((soh - 80.0) / annual_loss_rate, 0) if annual_loss_rate > 0 else 10.0
            months_to_eol = years_to_eol * 12

            if random.random() < 0.12:
                months_to_eol = random.uniform(1.0, 5.5) 

            if region not in regions:
                regions[region] = {
                    'region_name': region,
                    'total_bevs': 0, 'sum_odo': 0, 'sum_soh': 0, 'lithium_tons_at_risk': 0.0,
                    'cohorts': {'0-3_months': 0, '3-6_months': 0, '6-12_months': 0, 'safe': 0}
                }

            reg = regions[region]
            
            # --- FIX: Scale up the real numbers for the AI ---
            reg['total_bevs'] += self.SCALE_FACTOR
            reg['sum_odo'] += (odo * self.SCALE_FACTOR)
            reg['sum_soh'] += (soh * self.SCALE_FACTOR)

            if months_to_eol <= 12:
                reg['lithium_tons_at_risk'] += (0.5 * self.SCALE_FACTOR)

            if months_to_eol <= 3:
                reg['cohorts']['0-3_months'] += self.SCALE_FACTOR
            elif months_to_eol <= 6:
                reg['cohorts']['3-6_months'] += self.SCALE_FACTOR
            elif months_to_eol <= 12:
                reg['cohorts']['6-12_months'] += self.SCALE_FACTOR
            else:
                reg['cohorts']['safe'] += self.SCALE_FACTOR

        for r in regions.values():
            if r['total_bevs'] > 0:
                r['avg_odo'] = r['sum_odo'] / r['total_bevs']
                r['avg_soh'] = r['sum_soh'] / r['total_bevs']
            del r['sum_odo']
            del r['sum_soh']

        return list(regions.values())