"""
Fleet Data Enrichment Seeder
Adds missing consumer-facing data (plates, driver names, insurance, components, maintenance)
to the partner's enterprise DB using the DatabaseManager pattern.
"""
import sqlite3
import random
import string
from datetime import datetime, timedelta
from models.data_manager.database_manager import DatabaseManager

# ── Italian Name Pools ────────────────────────────────────────────────────
FIRST_NAMES_M = ["Marco","Andrea","Luca","Giuseppe","Alessandro","Francesco","Matteo","Roberto",
    "Antonio","Davide","Stefano","Paolo","Simone","Lorenzo","Fabio","Enrico","Riccardo",
    "Gianluca","Massimo","Claudio","Alberto","Daniele","Federico","Giorgio","Leonardo",
    "Emanuele","Vincenzo","Nicola","Salvatore","Pietro","Carlo","Michele","Giacomo"]
FIRST_NAMES_F = ["Maria","Giulia","Chiara","Sara","Laura","Valentina","Francesca","Alessia",
    "Martina","Elisa","Elena","Silvia","Paola","Anna","Federica","Cristina","Monica",
    "Roberta","Claudia","Beatrice","Sofia","Aurora","Camilla","Serena","Ilaria"]
LAST_NAMES = ["Rossi","Russo","Ferrari","Esposito","Bianchi","Romano","Colombo","Ricci","Marino",
    "Greco","Bruno","Gallo","Conti","De Luca","Mancini","Costa","Giordano","Rizzo","Lombardi",
    "Moretti","Barbieri","Fontana","Santoro","Mariani","Rinaldi","Caruso","Ferrara","Galli",
    "Martini","Leone","Longo","Gentile","Martinelli","Vitale","Pellegrini","Parodi","Melis"]

COLORS = ["Nero Ribelle","Bianco Perla","Grigio Titanio","Blu Notte","Rosso Corsa",
    "Verde Petrolio","Argento Metallico","Blu Emozione","Grigio Lava","Bianco Ghiaccio",
    "Nero Vulcano","Rosso Magma","Blu Cobalto","Grigio Grafite","Marrone Terra"]

INSURERS = ["UnipolSai","Generali","Allianz","AXA","Zurich","Sara Assicurazioni",
    "Cattolica","Vittoria","Reale Mutua","Groupama"]
POLICY_TYPES = ["CASKO","RCA","CASKO","RCA","CASKO","RCA"]  # weighted toward RCA

PLATE_LETTERS = "ABCDEFGHJKLMNPRSTUVWXYZ"  # Italian plate valid letters

class FleetDataSeeder:
    """Enriches the partner's DB with realistic fleet data for the registry UI."""

    @staticmethod
    def run():
        """Main entry point — call once to enrich the entire fleet."""
        conn = DatabaseManager.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("🌱 Fleet Data Seeder: Starting enrichment...")

        # Step 1: Add missing columns
        FleetDataSeeder._add_missing_columns(cursor)
        conn.commit()

        # Step 2: Create missing tables
        FleetDataSeeder._create_missing_tables(cursor)
        conn.commit()

        # Step 3: Generate plate numbers, driver names, colors, insurance for all vehicles
        FleetDataSeeder._enrich_vehicles(cursor)
        conn.commit()

        # Step 4: Generate components for vehicles that don't have them
        FleetDataSeeder._seed_components(cursor)
        conn.commit()

        # Step 5: Generate maintenance history
        FleetDataSeeder._seed_maintenance(cursor)
        conn.commit()

        conn.close()
        print("✅ Fleet Data Seeder: Complete!")

    @staticmethod
    def _add_missing_columns(cursor):
        """Dynamically add consumer columns if they don't exist."""
        cols = [
            ("vehicles", "driver_name", "TEXT"),
            ("vehicles", "policy_number", "TEXT"),
            ("vehicles", "policy_type", "TEXT"),
            ("vehicles", "insurer", "TEXT"),
            ("vehicles", "premium_eur", "REAL"),
            ("vehicles", "policy_start", "TEXT"),
            ("vehicles", "policy_expiry", "TEXT"),
            ("vehicles", "policy_status", "TEXT"),
            ("vehicles", "telematics_discount", "REAL"),
            ("vehicles", "claims_count", "INTEGER"),
            ("vehicles", "has_blackbox", "INTEGER"),
            ("vehicles", "body_type", "TEXT"),
            ("vehicles", "country", "TEXT"),
            ("vehicles", "city", "TEXT"),
            ("vehicles", "power_hp", "INTEGER"),
            ("vehicles", "displacement_cc", "INTEGER"),
            ("vehicles", "weight_kg", "INTEGER"),
            ("vehicles", "registration_date", "TEXT"),
            ("vehicles", "status", "TEXT"),
            ("car_models", "displacement_cc", "INTEGER"),
            ("car_models", "power_hp", "INTEGER"),
            ("car_models", "weight_kg", "INTEGER"),
        ]
        for table, col, ctype in cols:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ctype}")
                print(f"  ➕ Added {table}.{col}")
            except sqlite3.OperationalError:
                pass  # Column already exists

    @staticmethod
    def _create_missing_tables(cursor):
        """Create maintenance_events and investigations tables."""
        cursor.execute("""CREATE TABLE IF NOT EXISTS maintenance_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_vin TEXT NOT NULL,
            event_date TEXT,
            event_type TEXT,
            description TEXT,
            mileage_km INTEGER,
            cost_eur REAL,
            facility TEXT,
            severity TEXT DEFAULT 'info',
            FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin)
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT,
            vehicle_vin TEXT NOT NULL,
            incident_date TEXT,
            incident_type TEXT,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            fraud_risk_score REAL DEFAULT 0,
            description TEXT,
            FOREIGN KEY (vehicle_vin) REFERENCES vehicles(vin)
        )""")
        print("  ✅ maintenance_events and investigations tables ready")

    @staticmethod
    def _enrich_vehicles(cursor):
        """Generate plates, driver names, colors, insurance for all vehicles."""
        # Get vehicles that need enrichment
        vins = cursor.execute(
            "SELECT vin, driver_age, driver_gender, region_name, vehicle_category FROM vehicles WHERE driver_name IS NULL"
        ).fetchall()
        
        if not vins:
            print("  ⏭️  All vehicles already enriched — skipping")
            return

        print(f"  🔧 Enriching {len(vins)} vehicles...")
        
        used_plates = set()
        # Keep existing plate
        for r in cursor.execute("SELECT plate_number FROM vehicles WHERE plate_number IS NOT NULL").fetchall():
            used_plates.add(r[0])

        region_cities = {
            "Lombardia": ["Milano","Bergamo","Brescia","Como","Monza"],
            "Lazio": ["Roma","Latina","Frosinone","Viterbo"],
            "Campania": ["Napoli","Salerno","Caserta","Avellino"],
            "Sicilia": ["Palermo","Catania","Messina","Siracusa"],
            "Piemonte": ["Torino","Novara","Alessandria","Cuneo"],
            "Veneto": ["Venezia","Verona","Padova","Vicenza"],
            "Emilia-Romagna": ["Bologna","Modena","Parma","Reggio Emilia"],
            "Toscana": ["Firenze","Pisa","Siena","Livorno"],
            "Puglia": ["Bari","Lecce","Taranto","Foggia"],
            "Liguria": ["Genova","La Spezia","Savona","Imperia"],
            "Calabria": ["Cosenza","Catanzaro","Reggio Calabria"],
            "Sardegna": ["Cagliari","Sassari","Olbia"],
            "Marche": ["Ancona","Pesaro","Macerata"],
            "Abruzzo": ["L'Aquila","Pescara","Chieti"],
            "Friuli-Venezia Giulia": ["Trieste","Udine","Pordenone"],
            "Trentino-Alto Adige": ["Trento","Bolzano"],
            "Umbria": ["Perugia","Terni"],
            "Basilicata": ["Potenza","Matera"],
            "Molise": ["Campobasso","Isernia"],
            "Valle d'Aosta": ["Aosta"],
        }

        # Model specs for realistic data
        model_specs = {
            "Grecale Folgore": {"hp": 557, "cc": 0, "kg": 2260},
            "Model 3": {"hp": 283, "cc": 0, "kg": 1830},
            "500e": {"hp": 118, "cc": 0, "kg": 1365},
            "Golf": {"hp": 150, "cc": 1498, "kg": 1350},
            "X5": {"hp": 286, "cc": 2998, "kg": 2195},
            "Yaris": {"hp": 116, "cc": 1490, "kg": 1130},
        }

        # Update model specs once
        for model_name, specs in model_specs.items():
            cursor.execute(
                "UPDATE car_models SET power_hp=?, displacement_cc=?, weight_kg=? WHERE model_name=?",
                (specs["hp"], specs["cc"], specs["kg"], model_name)
            )

        batch = []
        for v in vins:
            vin = v["vin"]
            gender = v["driver_gender"] or random.choice(["Male", "Female"])
            age = v["driver_age"] or random.randint(22, 72)
            region = v["region_name"] or "Lombardia"

            # Generate plate
            plate = FleetDataSeeder._gen_plate(used_plates)
            used_plates.add(plate)

            # Generate driver name
            if gender == "Female":
                name = f"{random.choice(FIRST_NAMES_F)} {random.choice(LAST_NAMES)}"
            else:
                name = f"{random.choice(FIRST_NAMES_M)} {random.choice(LAST_NAMES)}"

            color = random.choice(COLORS)
            city = random.choice(region_cities.get(region, ["Roma"]))

            # Insurance
            insurer = random.choice(INSURERS)
            policy_type = random.choice(POLICY_TYPES)
            base_premium = random.randint(350, 2200)
            
            # Driving score affects discount
            telem = cursor.execute("SELECT driving_score FROM vehicle_telemetry WHERE vin=?", (vin,)).fetchone()
            score = telem["driving_score"] if telem else 50
            discount = round(min(25, max(0, (score - 40) * 0.4)), 1) if score > 40 else 0
            premium = round(base_premium * (1 - discount/100), 2)
            
            claims = 0 if score > 70 else (random.choice([0,0,0,1]) if score > 40 else random.choice([0,1,1,2]))
            
            policy_start = f"202{random.randint(3,5)}-{random.randint(1,12):02d}-01"
            policy_expiry = f"202{random.randint(6,7)}-{random.randint(1,12):02d}-01"
            policy_number = f"POL-{random.randint(2023,2025)}-{random.randint(10000,99999)}"
            
            has_bb = 1 if random.random() < 0.55 else 0

            batch.append((
                plate, name, color, city, "IT", policy_number, policy_type, insurer,
                premium, policy_start, policy_expiry, "active", discount, claims,
                has_bb, "active", vin
            ))

        cursor.executemany("""UPDATE vehicles SET 
            plate_number=?, driver_name=?, color=?, city=?, country=?,
            policy_number=?, policy_type=?, insurer=?, premium_eur=?,
            policy_start=?, policy_expiry=?, policy_status=?, telematics_discount=?,
            claims_count=?, has_blackbox=?, status=?
            WHERE vin=?""", batch)

        print(f"  ✅ Enriched {len(batch)} vehicles with plates, names, insurance")

    @staticmethod
    def _gen_plate(used):
        """Generate a unique Italian plate number (XX 000 XX format)."""
        while True:
            p1 = random.choice(PLATE_LETTERS) + random.choice(PLATE_LETTERS)
            num = f"{random.randint(0,999):03d}"
            p2 = random.choice(PLATE_LETTERS) + random.choice(PLATE_LETTERS)
            plate = f"{p1} {num} {p2}"
            if plate not in used:
                return plate

    @staticmethod
    def _seed_components(cursor):
        """Generate brake_pad and tire components for vehicles that lack them."""
        # Get VINs that have NO components yet
        existing = set(r[0] for r in cursor.execute(
            "SELECT DISTINCT vehicle_vin FROM components"
        ).fetchall())
        existing_tires = set(r[0] for r in cursor.execute(
            "SELECT DISTINCT vin FROM mounted_tires"
        ).fetchall())

        # Get all VINs with telemetry (these are real simulated vehicles)
        all_vins = cursor.execute("""
            SELECT v.vin, vt.driving_score, vt.current_odometer_km, cm.powertrain
            FROM vehicles v
            JOIN vehicle_telemetry vt ON v.vin = vt.vin
            JOIN car_models cm ON v.model_id = cm.id
        """).fetchall()

        comp_batch = []
        tire_batch = []
        bp_id = cursor.execute("SELECT id FROM tire_blueprints LIMIT 1").fetchone()
        bp_id = bp_id[0] if bp_id else 1

        for v in all_vins:
            vin = v["vin"]
            score = v["driving_score"] or 50
            odo = v["current_odometer_km"] or 10000
            pt = v["powertrain"] or "ICE"

            if vin not in existing:
                # Brake pads — wear correlates with driving score (inverse)
                front_wear = round(max(5, min(95, random.gauss(65 - score * 0.4, 15))), 1)
                rear_wear = round(max(5, min(95, random.gauss(70 - score * 0.35, 18))), 1)
                comp_batch.append((vin, "brake_pad", "front", front_wear, "installed"))
                comp_batch.append((vin, "brake_pad", "rear", rear_wear, "installed"))

                # EV battery for BEV/Hybrid
                if pt in ("BEV", "Hybrid"):
                    batt_deg = round(max(1, min(30, odo / 15000 + random.gauss(0, 2))), 1)
                    comp_batch.append((vin, "ev_battery", "main", batt_deg, "installed"))

            if vin not in existing_tires:
                # 4 tires with varying wear
                for pos in ["FL", "FR", "RL", "RR"]:
                    base_tread = 8.0  # Starting depth
                    # Rear tires wear faster, aggressive drivers more
                    wear_factor = 1.2 if pos.startswith("R") else 1.0
                    wear_factor *= (1.3 if score < 40 else 1.0 if score < 70 else 0.85)
                    tread = round(max(1.2, base_tread - (odo / 8000) * wear_factor + random.gauss(0, 0.5)), 1)
                    tire_batch.append((vin, bp_id, pos, max(0, odo - random.randint(5000, 20000)), tread))

        if comp_batch:
            cursor.executemany(
                "INSERT INTO components (vehicle_vin, category, position, wear_percent, status) VALUES (?,?,?,?,?)",
                comp_batch
            )
        if tire_batch:
            cursor.executemany(
                "INSERT INTO mounted_tires (vin, blueprint_id, position, mounting_odometer_km, current_tread_depth_mm) VALUES (?,?,?,?,?)",
                tire_batch
            )
        print(f"  ✅ Seeded {len(comp_batch)} components and {len(tire_batch)} tires")

    @staticmethod
    def _seed_maintenance(cursor):
        """Generate maintenance history for a subset of vehicles."""
        count = cursor.execute("SELECT COUNT(*) FROM maintenance_events").fetchone()[0]
        if count > 0:
            print(f"  ⏭️  {count} maintenance events already exist — skipping")
            return

        # Get vehicles with critical components
        vins = cursor.execute("""
            SELECT DISTINCT v.vin, vt.current_odometer_km, vt.driving_score
            FROM vehicles v
            JOIN vehicle_telemetry vt ON v.vin = vt.vin
            LIMIT 500
        """).fetchall()

        events_pool = [
            ("scheduled", "Routine VSI diagnostic completed", "info"),
            ("scheduled", "Annual service at authorized dealer", "info"),
            ("scheduled", "Oil change and filter replacement", "info"),
            ("notification", "Brake wear notification sent to driver", "notification"),
            ("alert", "Tire tread below recommended threshold", "warning"),
            ("alert", "VSI critical: aggressive driving pattern detected", "warning"),
            ("critical", "Collision reported. Telemetry locked.", "critical"),
            ("scheduled", "Tire rotation performed at UnipolService network", "info"),
            ("notification", "Telematics discount eligibility notification sent", "notification"),
            ("scheduled", "Brake pad replacement at authorized dealer", "info"),
        ]

        batch = []
        for v in vins:
            vin = v["vin"]
            score = v["driving_score"] or 50
            odo = v["current_odometer_km"] or 10000

            num_events = random.randint(1, 5) if score < 50 else random.randint(1, 3)
            for _ in range(num_events):
                evt = random.choice(events_pool)
                days_ago = random.randint(30, 800)
                date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                mileage = max(1000, odo - random.randint(5000, 40000))
                cost = round(random.uniform(50, 600), 2) if evt[0] == "scheduled" else 0
                facility = random.choice(["UnipolService Milano","UnipolService Roma","Maserati Service Center",
                    "AutoMecc Torino","Euromaster","Driver Center","Quick Service Napoli"]) if evt[0] == "scheduled" else ""
                batch.append((vin, date, evt[0], evt[1], mileage, cost, facility, evt[2]))

        cursor.executemany(
            "INSERT INTO maintenance_events (vehicle_vin, event_date, event_type, description, mileage_km, cost_eur, facility, severity) VALUES (?,?,?,?,?,?,?,?)",
            batch
        )
        print(f"  ✅ Seeded {len(batch)} maintenance events")


if __name__ == "__main__":
    FleetDataSeeder.run()
