import sys
import os

# Add the cycle_sync_app and website directories to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'cycle_sync_app'))

from website.cache_manager import init_db, set_cache
from models.insurer_models.actuarial_model import ActuarialModel
from models.insurer_models.fleet_model import FleetModel

def run_precomputation():
    print("Initializing UI Cache Database...")
    init_db()

    print("Loading models (this might take a while)...")
    actuarial_model = ActuarialModel()
    fleet_model = FleetModel()

    print("Precomputing actuarial summary...")
    summary = actuarial_model.generate_executive_summary(account_id=0)
    set_cache('actuarial_summary', summary)

    print("Precomputing demographic deep dive...")
    deep_dive = actuarial_model.get_demographic_deep_dive()
    set_cache('demographic_deep_dive', deep_dive)

    print("Precomputing asset risk portfolio...")
    portfolio = actuarial_model.get_asset_risk_portfolio()
    set_cache('asset_risk_portfolio', portfolio)

    print("Precomputing ESG sustainability metrics...")
    esg = actuarial_model.get_esg_sustainability_metrics()
    set_cache('esg_metrics', esg)

    print("Precomputing fleet regional KPIs...")
    regional_kpis = fleet_model.get_regional_kpis(0)
    set_cache('fleet_regional_kpis', regional_kpis)

    print("Precomputing BEV regional analytics...")
    bev_analytics = fleet_model.get_bev_regional_analytics(account_id=0)
    set_cache('bev_regional_analytics', bev_analytics)

    print("Precomputation completed successfully! The UI will now load instantly.")

if __name__ == "__main__":
    run_precomputation()
