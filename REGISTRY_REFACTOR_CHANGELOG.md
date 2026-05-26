# Registry Tab Refactor — Files Changed

## Backend (Python)

| File | Action | Description |
|------|--------|-------------|
| `cycle_sync_app/models/fleet_data_seeder.py` | **NEW** | Data enrichment module — adds plates, driver names, colors, insurance, components, tires, maintenance to all 3480 vehicles using `DatabaseManager.get_connection()` |
| `website/routers/vehicle_api.py` | **MODIFIED** (lines 247–480) | Rewrote 6 fleet registry API endpoints to return full data: driver names, insurance fields, blackbox status, passport with insurance/telemetry/components/maintenance |

## Frontend (HTML/JS)

| File | Action | Description |
|------|--------|-------------|
| `website/static/partials/telemetry_tab.html` | **MODIFIED** (lines 46–67) | Added Insurance & Blackbox filter dropdowns, added green "+ Register" button, changed filter layout from grid to flex-wrap |

## Database Changes (via fleet_data_seeder.py)

**New columns on `vehicles`:** `driver_name`, `policy_number`, `policy_type`, `insurer`, `premium_eur`, `policy_start`, `policy_expiry`, `policy_status`, `telematics_discount`, `claims_count`, `has_blackbox`, `body_type`, `country`, `city`, `power_hp`, `displacement_cc`, `weight_kg`, `registration_date`, `status`

**New columns on `car_models`:** `displacement_cc`, `power_hp`, `weight_kg`

**New tables:** `maintenance_events`, `investigations`

## Data Seeded
- 3,480 Italian plate numbers + driver names + colors + cities
- 8,719 components (brake pads front/rear + EV batteries)
- 13,916 tires (4 per vehicle with realistic tread depth)
- 1,060 maintenance events
- Insurance data for all vehicles (UnipolSai/Generali/Allianz/etc)
