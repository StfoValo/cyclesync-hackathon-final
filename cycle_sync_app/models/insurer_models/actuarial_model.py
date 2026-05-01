import random
from models.data_manager.database_manager import DatabaseManager
from models.insurer_models.fleet_model import FleetModel

class ActuarialModel:
    def __init__(self):
        self.fleet_model = FleetModel()
        
        # Italian RCA Baseline Metrics (Euros)
        self.BASE_PREMIUM = 450.0 
        
        # Financial Multipliers based on Behavioral Telematics
        self.DISCOUNT_SAFE = 0.85      # -15% for Score > 85
        self.MULTIPLIER_MODERATE = 1.0 # 0% for Score 60-84
        self.MALUS_RISK = 1.20         # +20% for Score < 60
        
        # Statistical Accident Probabilities per Cohort
        self.PROB_SAFE = 0.032
        self.PROB_MODERATE = 0.055
        self.PROB_RISK = 0.125

    def generate_executive_summary(self, account_id: int):
        regional_kpis = self.fleet_model.get_regional_kpis(account_id)
        
        total_fleet = 0
        total_safe = 0
        total_mod = 0
        total_risk = 0
        
        regional_financials = []

        for r in regional_kpis:
            cars = r['total_cars']
            safe = r['risk_safe']
            mod = r['risk_moderate']
            risk = r['risk_high']
            
            total_fleet += cars
            total_safe += safe
            total_mod += mod
            total_risk += risk
            
            reg_revenue = (safe * self.BASE_PREMIUM * self.DISCOUNT_SAFE) + \
                          (mod * self.BASE_PREMIUM * self.MULTIPLIER_MODERATE) + \
                          (risk * self.BASE_PREMIUM * self.MALUS_RISK)
                          
            # 1. Projected Claims (with Telematics behavioral shifts)
            reg_accidents = (safe * self.PROB_SAFE) + (mod * self.PROB_MODERATE) + (risk * self.PROB_RISK)
            
            # --- FIX: 2. Simulate Current Registered Claims ---
            # Assume historical baseline (5.5%) with a +/- 5% real-world variance
            registered_claims = cars * self.PROB_MODERATE * random.uniform(0.95, 1.05)
            
            regional_financials.append({
                "region": r['region_name'],
                "total_cars": cars,
                "revenue_eur": reg_revenue,
                "projected_accidents": int(reg_accidents),
                "registered_claims": int(registered_claims), # <--- NEW FIELD
                "high_risk_ratio": (risk / cars) if cars > 0 else 0
            })

        # 3. Calculate Global Portfolio KPIs
        if total_fleet == 0:
            return None

        total_revenue = (total_safe * self.BASE_PREMIUM * self.DISCOUNT_SAFE) + \
                        (total_mod * self.BASE_PREMIUM * self.MULTIPLIER_MODERATE) + \
                        (total_risk * self.BASE_PREMIUM * self.MALUS_RISK)
                        
        avg_premium = total_revenue / total_fleet
        avg_discount = ((avg_premium / self.BASE_PREMIUM) - 1.0) * 100 # e.g., -8.4%

        # Calculate how many accidents we PREVENTED by having safe drivers (compared to a baseline 5.5% for everyone)
        baseline_accidents = total_fleet * self.PROB_MODERATE
        actual_projected_accidents = (total_safe * self.PROB_SAFE) + (total_mod * self.PROB_MODERATE) + (total_risk * self.PROB_RISK)
        claims_reduction_pct = ((baseline_accidents - actual_projected_accidents) / baseline_accidents) * 100

        # Simulate Preventative Alerts (Tire/Brake warnings sent to High Risk drivers)
        preventative_alerts_issued = int(total_risk * 0.45) # Assume 45% of high-risk drivers triggered an intervention alert

        return {
            "kpis": {
                "total_monitored_fleet": total_fleet,
                "average_premium_eur": avg_premium,
                "average_discount_pct": avg_discount,
                "claims_reduction_pct": claims_reduction_pct,
                "preventative_alerts": preventative_alerts_issued
            },
            "regional_breakdown": sorted(regional_financials, key=lambda x: x['high_risk_ratio'], reverse=True)
        }

    def get_demographic_deep_dive(self):
        """Aggregates claims data by Age, Gender, Vehicle Type, Vehicle Age, and Behavior."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # --- FIX: Added SQLite julianday() math to dynamically calculate RCA Vehicle Age Brackets ---
        cursor.execute(f'''
            SELECT 
                v.vehicle_category,
                v.driver_gender,
                CASE 
                    WHEN v.driver_age BETWEEN 18 AND 24 THEN '18-24'
                    WHEN v.driver_age BETWEEN 25 AND 34 THEN '25-34'
                    WHEN v.driver_age BETWEEN 35 AND 44 THEN '35-44'
                    WHEN v.driver_age BETWEEN 45 AND 54 THEN '45-54'
                    WHEN v.driver_age BETWEEN 55 AND 64 THEN '55-64'
                    ELSE '65+' END as age_group,
                CASE 
                    WHEN (julianday('now') - julianday(v.production_date))/365.25 <= 2 THEN '0-2 Years (New)'
                    WHEN (julianday('now') - julianday(v.production_date))/365.25 <= 5 THEN '3-5 Years (Recent)'
                    WHEN (julianday('now') - julianday(v.production_date))/365.25 <= 9 THEN '6-9 Years (Average)'
                    ELSE '10+ Years (Old)' END as vehicle_age_group,
                SUM(CASE WHEN t.driving_score >= 85 THEN 1 ELSE 0 END) * {self.fleet_model.SCALE_FACTOR} as safe_count,
                SUM(CASE WHEN t.driving_score >= 60 AND t.driving_score < 85 THEN 1 ELSE 0 END) * {self.fleet_model.SCALE_FACTOR} as mod_count,
                SUM(CASE WHEN t.driving_score < 60 THEN 1 ELSE 0 END) * {self.fleet_model.SCALE_FACTOR} as risk_count
            FROM vehicles v
            JOIN vehicle_telemetry t ON v.vin = t.vin
            WHERE v.driver_age IS NOT NULL AND v.vehicle_category IS NOT NULL
            GROUP BY v.vehicle_category, v.driver_gender, age_group, vehicle_age_group
        ''')
        
        results = cursor.fetchall()
        conn.close()

        payload = {
            "genders": {"Male": 0, "Female": 0},
            "age_groups": {"18-24": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55-64": 0, "65+": 0},
            "vehicle_types": {},
            "vehicle_ages": {"0-2 Years (New)": 0, "3-5 Years (Recent)": 0, "6-9 Years (Average)": 0, "10+ Years (Old)": 0},
            "behaviors": {"Safe (Eco)": 0, "Moderate": 0, "High Risk (Harsh)": 0}
        }

        for row in results:
            veh_cat, gender, age_group, veh_age_group, safe, mod, risk = row
            
            base_claims = (safe * self.PROB_SAFE) + (mod * self.PROB_MODERATE) + (risk * self.PROB_RISK)
            
            safe_car_type = str(veh_cat).upper() if veh_cat else "UNKNOWN"
            
            # RCA Modifiers: Vehicle Type Risk
            type_modifiers = {
                'UTILITARIAN': 1.15, 'HATCHBACK': 1.00, 'SUV': 0.85, 'SEDAN': 0.90, 'SPORTSCAR': 1.40 
            }
            
            # --- FIX: RCA Modifiers: Vehicle Age Risk (Older cars fail more) ---
            age_modifiers = {
                '0-2 Years (New)': 0.95,
                '3-5 Years (Recent)': 1.00,
                '6-9 Years (Average)': 1.10,
                '10+ Years (Old)': 1.25
            }
            
            # The final double-weighted claims projection
            projected_claims = int(base_claims * type_modifiers.get(safe_car_type, 1.0) * age_modifiers.get(veh_age_group, 1.0))
            
            if gender in payload["genders"]: payload["genders"][gender] += projected_claims
            if age_group in payload["age_groups"]: payload["age_groups"][age_group] += projected_claims
            if veh_age_group in payload["vehicle_ages"]: payload["vehicle_ages"][veh_age_group] += projected_claims
            payload["vehicle_types"][safe_car_type] = payload["vehicle_types"].get(safe_car_type, 0) + projected_claims
            
            behavior_mod = type_modifiers.get(safe_car_type, 1.0) * age_modifiers.get(veh_age_group, 1.0)
            payload["behaviors"]["Safe (Eco)"] += int((safe * self.PROB_SAFE) * behavior_mod)
            payload["behaviors"]["Moderate"] += int((mod * self.PROB_MODERATE) * behavior_mod)
            payload["behaviors"]["High Risk (Harsh)"] += int((risk * self.PROB_RISK) * behavior_mod)

        return payload

    def get_asset_risk_portfolio(self):
        """Aggregates physical health of Brakes, Tires, and Batteries globally AND regionally."""
        regional_kpis = self.fleet_model.get_regional_kpis(0) 
        
        portfolio = {
            "metrics": {
                "avg_vsi_score": 0.0,
                "total_critical_assets": 0,
                "projected_hardware_claims_eur": 0.0
            },
            "global": {
                "overall_vsi": {"Safe": 0, "Warning": 0, "Critical": 0},
                "brakes": {"Safe (>6mm)": 0, "Warning (3-6mm)": 0, "Critical (<3mm)": 0},
                "tires": {"Safe (>4mm)": 0, "Warning (2-4mm)": 0, "Critical (<2mm)": 0}
            },
            "regional": []
        }
        
        total_cars = 0
        total_vsi_sum = 0
        
        for r in regional_kpis:
            cars = r['total_cars']
            if cars == 0: continue
            
            safe_pct = r['risk_safe'] / cars
            mod_pct = r['risk_moderate'] / cars
            risk_pct = r['risk_high'] / cars
            
            # --- Hardware Calculations ---
            b_crit = int(cars * risk_pct * 0.4) 
            b_warn = int(cars * (risk_pct * 0.6 + mod_pct * 0.3))
            b_safe = cars - b_crit - b_warn
            
            t_crit = int(cars * risk_pct * 0.3) 
            t_warn = int(cars * (risk_pct * 0.7 + mod_pct * 0.4))
            t_safe = cars - t_crit - t_warn
            
            v_crit = int(b_crit * 0.6 + t_crit * 0.4) 
            v_warn = int(b_warn * 0.6 + t_warn * 0.4)
            v_safe = cars - v_crit - v_warn
            
            # --- 1. Populate Global Sums ---
            portfolio["global"]["brakes"]["Critical (<3mm)"] += b_crit
            portfolio["global"]["brakes"]["Warning (3-6mm)"] += b_warn
            portfolio["global"]["brakes"]["Safe (>6mm)"] += b_safe
            
            portfolio["global"]["tires"]["Critical (<2mm)"] += t_crit
            portfolio["global"]["tires"]["Warning (2-4mm)"] += t_warn
            portfolio["global"]["tires"]["Safe (>4mm)"] += t_safe
            
            portfolio["global"]["overall_vsi"]["Critical"] += v_crit
            portfolio["global"]["overall_vsi"]["Warning"] += v_warn
            portfolio["global"]["overall_vsi"]["Safe"] += v_safe
            
            # --- FIX: 2. Populate Regional Array ---
            portfolio["regional"].append({
                "region": r['region_name'],
                "vsi": [v_safe, v_warn, v_crit],
                "brakes": [b_safe, b_warn, b_crit],
                "tires": [t_safe, t_warn, t_crit]
            })
            
            total_cars += cars
            total_vsi_sum += (v_safe * 85) + (v_warn * 60) + (v_crit * 30)

        if total_cars > 0:
            portfolio["metrics"]["avg_vsi_score"] = total_vsi_sum / total_cars
            portfolio["metrics"]["total_critical_assets"] = portfolio["global"]["overall_vsi"]["Critical"]
            portfolio["metrics"]["projected_hardware_claims_eur"] = portfolio["global"]["overall_vsi"]["Critical"] * 0.02 * 4500

        # Sort the regions so the ones with the most critical issues appear at the top
        portfolio["regional"].sort(key=lambda x: x["vsi"][2], reverse=True)

        return portfolio

    def simulate_campaign_conversion(self, region: str, payload_data: dict):
        """
        Simulates the real-world conversion rates of an AI-dispatched push notification campaign.
        """
        import random
        
        # 1. Base the volume on the actual critical assets in that region
        # We assume we only target the 'Critical' buckets
        critical_brakes = payload_data.get('Regional_Asset_Risk', {}).get('Braking_Systems', {}).get('Critical_Need_Replacement (<3mm)', 0)
        critical_tires = payload_data.get('Regional_Asset_Risk', {}).get('Tire_Wear', {}).get('Critical_Blowout_Risk (<2mm)', 0)
        
        total_targeted = critical_brakes + critical_tires
        
        # If there's no data, return a generic low simulation
        if total_targeted == 0:
            total_targeted = random.randint(500, 2000)

        # 2. Actuarial Conversion Math (Industry Averages)
        # 35% Open Rate, 12% Click-Through Rate (CTR), 4% Actual Booking Rate
        open_rate = random.uniform(0.32, 0.45)
        ctr = random.uniform(0.08, 0.15)
        booking_rate = random.uniform(0.03, 0.06)

        opened = int(total_targeted * open_rate)
        clicked = int(opened * ctr)
        booked = int(clicked * booking_rate)
        
        # Financial Impact (Assume averting a crash saves €4500, but paying for a discount costs €50)
        claims_prevented_eur = booked * 4500 * self.PROB_RISK
        campaign_cost_eur = booked * 50

        return {
            "region": region,
            "funnel": {
                "sent": total_targeted,
                "opened": opened,
                "clicked": clicked,
                "booked": booked
            },
            "financials": {
                "roi_eur": claims_prevented_eur - campaign_cost_eur,
                "conversion_rate_pct": (booked / total_targeted * 100) if total_targeted > 0 else 0
            }
        }

    def get_esg_sustainability_metrics(self):
        """
        Calculates Fleet Emissions (based on the Scientific Reports Virtual Sensor paper)
        and tracks the Circular Economy ledger for component Second Life.
        """
        import random
        
        # 1. EMISSIONS MODELING (Baseline Euro Class vs. Telematics Reality)
        # Using the convex polynomial curve concept: driving at 'Green Speeds' (50-75 km/h) 
        # with smooth braking drastically reduces CO2 compared to standard Euro class baseline.
        
        total_fleet = 8800000 # Unipol simulated fleet
        avg_km_per_year = 11500
        
        # Baseline CO2 (if we only looked at the Euro Class on the registration document)
        baseline_co2_kg_per_car = 1450  
        total_baseline_tons = (total_fleet * baseline_co2_kg_per_car) / 1000
        
        # Telematics Reality (Factoring in Eco-Coaching, Green Speeds, and smoothed acceleration)
        # Assume our app improves driving efficiency by a conservative 8.4%
        telematics_efficiency_gain = 0.084 
        real_co2_tons = total_baseline_tons * (1 - telematics_efficiency_gain)
        co2_saved_tons = total_baseline_tons - real_co2_tons

        # 2. CIRCULAR ECONOMY LEDGER (From Assembly Line to Second Life)
        # Mocking the data generated by the AI routing drivers to our mechanic network
        tires_replaced = random.randint(120000, 150000)
        brakes_replaced = random.randint(200000, 250000)
        batteries_replaced = random.randint(4000, 6000) # BEV end of life
        
        payload = {
            "emissions": {
                "baseline_co2_tons": total_baseline_tons,
                "real_telematics_co2_tons": real_co2_tons,
                "co2_saved_tons": co2_saved_tons,
                "equivalent_trees_planted": int(co2_saved_tons * 45) # Approx 45 trees to absorb 1 ton of CO2
            },
            "circular_economy": {
                "recovered_tires": {
                    "total_units": tires_replaced,
                    "destinations": {
                        "Asphalt_Rubber_Granulate": int(tires_replaced * 0.60),
                        "Energy_Recovery": int(tires_replaced * 0.30),
                        "Landfill_Avoided": int(tires_replaced * 0.10)
                    }
                },
                "recovered_brakes": {
                    "total_units": brakes_replaced,
                    "destinations": {
                        "Scrap_Metal_Smelting": int(brakes_replaced * 0.85),
                        "Friction_Material_Repurposing": int(brakes_replaced * 0.15)
                    }
                },
                "recovered_ev_batteries": {
                    "total_units": batteries_replaced,
                    "destinations": {
                        "Grid_Stationary_Storage (Repurposed)": int(batteries_replaced * 0.55),
                        "Black_Mass_Extraction (Recycled)": int(batteries_replaced * 0.40),
                        "Hazardous_Waste": int(batteries_replaced * 0.05)
                    }
                }
            }
        }
        return payload