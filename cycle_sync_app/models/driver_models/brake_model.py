class BrakeModel:
    def estimate_pad_life(self, current_odo_km: int, driving_score: int):
        """
        Calculates brake pad health.
        Lower driving score = more harsh G-force braking = exponentially faster wear.
        """
        NEW_PAD_MM = 12.0
        CRITICAL_PAD_MM = 2.0
        
        # A perfectly driven car gets 70k km out of brakes. A harsh driver gets 30k.
        expected_lifespan = 30000 + (40000 * (driving_score / 100))
        
        wear_ratio = min(current_odo_km / expected_lifespan, 1.0)
        current_thickness = NEW_PAD_MM - (wear_ratio * (NEW_PAD_MM - CRITICAL_PAD_MM))
        
        # Calculate health percentage
        health_pct = max(0.0, (current_thickness - CRITICAL_PAD_MM) / (NEW_PAD_MM - CRITICAL_PAD_MM) * 100)
        
        return {
            "current_thickness_mm": round(current_thickness, 1),
            "health_pct": round(health_pct, 1),
            "is_critical": health_pct < 15.0
        }