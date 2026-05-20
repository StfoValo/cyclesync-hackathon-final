from fastapi import APIRouter, Body
from models.data_manager.database_manager import DatabaseManager
from models.driver_models.brake_model import BrakeModel
from models.driver_models.tire_model import TireModel
from fastapi import Body

router = APIRouter()

@router.get("/api/driver/{driver_id}")
def get_driver_profile(driver_id: int):
    """
    Get driver profile and their linked garage. 
    Reads LIVE data directly from cyclesync.db.
    """
    print(f"🚦 [API HIT] /api/driver/{driver_id} called.")
    
    try:
        conn = DatabaseManager.get_connection()
        conn.row_factory = __import__('sqlite3').Row 
        cursor = conn.cursor()
        
        # 1. Fetch Driver Profile
        driver = cursor.execute(
            "SELECT * FROM driver_accounts WHERE id=?", (driver_id,)
        ).fetchone()
        
        if not driver:
            conn.close()
            return {"error": "Driver not found"}
            
        # 2. Fetch Linked Vehicles
        vehicles = cursor.execute("""
            SELECT 
                v.vin, v.plate_number, cm.model_name, cm.manufacturer, 
                v.production_date, v.color, cm.powertrain, v.vehicle_category,
                vt.driving_score, vt.current_odometer_km
            FROM driver_vehicles dv
            JOIN vehicles v ON dv.vin = v.vin
            JOIN car_models cm ON v.model_id = cm.id
            LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
            WHERE dv.driver_id = ?
            ORDER BY dv.added_at
        """, (driver_id,)).fetchall()
        
        conn.close()

        # 3. Format the response and dynamically map the images!
        formatted_vehicles = []
        for v in vehicles:
            # Safely format strings: 'Maserati' -> 'maserati', 'Grecale Folgore' -> 'grecale_folgore'
            mfr_clean = (v["manufacturer"] or "unknown").lower().replace(" ", "_")
            mdl_clean = (v["model_name"] or "unknown").lower().replace(" ", "_")
            
            # --- THE FIX: Updated to .webp for the car photo ---
            photo_url = f"/storage/car_photos/{mfr_clean}_{mdl_clean}.webp"
            
            # (If your maserati logo is actually a .png, change this next line to .png)
            logo_url = f"/storage/logos/{mfr_clean}_logo.jpg" 
            
            formatted_vehicles.append({
                "vin": v["vin"],
                "plate": v["plate_number"] or "N/A",
                "model": v["model_name"],
                "manufacturer": v["manufacturer"],
                "year": int(v["production_date"][:4]) if v["production_date"] else None,
                "color": v["color"],
                "powertrain": v["powertrain"],
                "body_type": v["vehicle_category"],
                "vsi_score": v["driving_score"],
                "odometer_km": v["current_odometer_km"],
                "is_pinned": v["vin"] == driver["pinned_vin"],
                "photo_url": photo_url,
                "logo_url": logo_url
            })
        
        print(f"✅ [SUCCESS] Found {len(formatted_vehicles)} linked vehicles.")
        
        return {
            "id": driver["id"],
            "email": driver["email"],
            "display_name": driver["display_name"],
            "phone": driver["phone"],
            "pinned_vin": driver["pinned_vin"],
            "vehicles": formatted_vehicles
        }
        
    except Exception as e:
        print(f"🚨 [CRITICAL DB ERROR]: {str(e)}")
        return {"error": f"Database failure: {str(e)}"}

@router.get("/api/driver/vehicle/{vin}/component-life")
def get_component_lifecycle(vin: str):
    """
    Evaluates telemetry against engineering models to estimate 
    GRANULAR component life (individual tires, front/rear brakes).
    """
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    
    # 1. Fetch live telemetry
    telemetry = cursor.execute("SELECT * FROM vehicle_telemetry WHERE vin=?", (vin,)).fetchone()
    if not telemetry:
        conn.close()
        return {"error": "Vehicle or telemetry not found"}

    current_odo = telemetry["current_odometer_km"]
    driving_score = telemetry["driving_score"]

    # 2. Fetch Granular Tires (4 corners)
    tires = cursor.execute("""
        SELECT m.position, m.current_tread_depth_mm, b.starting_tread_depth_mm, b.expected_lifespan_km
        FROM mounted_tires m
        JOIN tire_blueprints b ON m.blueprint_id = b.id
        WHERE m.vin = ?
    """, (vin,)).fetchall()

    # 3. Fetch Granular Components (Brakes Front/Rear, Battery)
    other_comps = cursor.execute("""
        SELECT category, position, wear_percent 
        FROM components 
        WHERE vehicle_vin = ? AND status = 'installed'
    """, (vin,)).fetchall()
    
    conn.close()
    
    components_payload = []
    
    # 4. Process Tires Math
    TREAD_MIN = 1.6 # Legal minimum tread depth in mm
    for t in tires:
        start_tread = t["starting_tread_depth_mm"]
        curr_tread = t["current_tread_depth_mm"]
        lifespan = t["expected_lifespan_km"]
        
        # Calculate health % based on tread depth
        health_pct = max(0.0, min(100.0, ((curr_tread - TREAD_MIN) / (start_tread - TREAD_MIN)) * 100))
        est_km = max(0, int(lifespan * (health_pct / 100.0)))
        
        # Determine UI color state
        urgency = "critical" if health_pct < 20 else ("warning" if health_pct < 40 else "good")
        
        components_payload.append({
            "category": "tire",
            "position": t["position"], # 'FL', 'FR', 'RL', 'RR'
            "health_pct": round(health_pct, 1),
            "est_remaining_km": est_km,
            "urgency": urgency,
            "consequence": f"Battistrada residuo: {curr_tread}mm"
        })
        
    # 5. Process Brakes & Battery Math
    for c in other_comps:
        cat = c["category"]
        pos = c["position"]
        wear = c["wear_percent"] # In DB, wear is 0-100 (where 100 is fully worn)
        health_pct = max(0.0, 100.0 - wear)
        
        if cat == "brake_pad":
            # Dynamic lifespan based on driver score
            base_life = 30000 + (40000 * (driving_score / 100.0))
            est_km = int(base_life * (health_pct / 100.0))
            urgency = "critical" if health_pct < 15 else ("warning" if health_pct < 30 else "good")
            cons = "Sostituzione consigliata." if urgency != "good" else "Freni in ottime condizioni."
        else: # ev_battery
            est_km = int(150000 * (health_pct / 100.0))
            urgency = "critical" if health_pct < 70 else ("warning" if health_pct < 80 else "good")
            cons = "Nessuna anomalia termica."
            
        components_payload.append({
            "category": cat,
            "position": pos,
            "health_pct": round(health_pct, 1),
            "est_remaining_km": est_km,
            "urgency": urgency,
            "consequence": cons
        })

    # Return exactly what the JS expects
    return {
        "vsi_tips": [
            "Evita frenate brusche per allungare la vita delle pastiglie del 12%.",
            "Mantiene la pressione degli pneumatici a 2.3 bar per risparmiare il 5% di CO2."
        ],
        "components": components_payload
    }

@router.put("/api/driver/{driver_id}/pin/{vin}")
def pin_vehicle(driver_id: int, vin: str):
    """Updates the driver's default vehicle."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE driver_accounts SET pinned_vin=? WHERE id=?", (vin, driver_id))
    conn.commit()
    conn.close()
    return {"status": "ok", "pinned_vin": vin}

@router.post("/api/driver/{driver_id}/vehicles")
def link_vehicle(driver_id: int, data: dict = Body(...)):
    """Links a new vehicle to the driver's garage via VIN or Plate."""
    search = data.get("search", "").strip().upper().replace(" ", "").replace("-", "")
    if not search:
        return {"error": "Please provide a VIN or Plate number."}
        
    conn = DatabaseManager.get_connection()
    conn.row_factory = __import__('sqlite3').Row
    cursor = conn.cursor()
    
    # Check if the car exists in the enterprise database
    row = cursor.execute("""
        SELECT vin FROM vehicles 
        WHERE REPLACE(plate_number, ' ', '') = ? OR vin = ?
    """, (search, search)).fetchone()
    
    if not row:
        conn.close()
        return {"error": "Vehicle not found in the network."}
        
    vin = row["vin"]
    
    # Link it to the driver
    try:
        cursor.execute("INSERT INTO driver_vehicles (driver_id, vin) VALUES (?, ?)", (driver_id, vin))
        conn.commit()
    except Exception:
        conn.close()
        return {"error": "This vehicle is already in your garage."}
        
    conn.close()
    return {"status": "ok", "vin": vin}

@router.delete("/api/driver/{driver_id}/vehicles/{vin}")
def unlink_vehicle(driver_id: int, vin: str):
    """Removes a vehicle from the driver's garage."""
    conn = DatabaseManager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM driver_vehicles WHERE driver_id=? AND vin=?", (driver_id, vin))
    # If they deleted their pinned car, clear the pin
    cursor.execute("UPDATE driver_accounts SET pinned_vin=NULL WHERE id=? AND pinned_vin=?", (driver_id, vin))
    
    conn.commit()
    conn.close()
    return {"status": "ok"}