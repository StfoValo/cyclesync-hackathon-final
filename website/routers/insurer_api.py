from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import folium
from models.insurer_models.actuarial_model import ActuarialModel
from models.insurer_models.fleet_model import FleetModel

SERVICE_PROVIDERS = [
    {"name": "Autofficina Sprint", "type": "Officina", "lat": 45.5421, "lon": 9.2014, "region": "Lombardia"},
    {"name": "Pneus Master", "type": "Gommista", "lat": 41.8905, "lon": 12.4942, "region": "Lazio"},
    {"name": "Meccanica Elite", "type": "Officina", "lat": 37.5013, "lon": 15.0742, "region": "Sicilia"},
    {"name": "Garage Centrale", "type": "Officina", "lat": 40.8522, "lon": 14.2681, "region": "Campania"},
    {"name": "Tutto Gomme Nord", "type": "Gommista", "lat": 45.4381, "lon": 12.3185, "region": "Veneto"},
    {"name": "RiparaAuto 24h", "type": "Officina", "lat": 44.4949, "lon": 11.3426, "region": "Emilia-Romagna"},
    {"name": "Wheel Center Advanced", "type": "Gommista", "lat": 45.0703, "lon": 7.6869, "region": "Piemonte"},
    {"name": "Officina del Sole", "type": "Officina", "lat": 41.1171, "lon": 16.8719, "region": "Puglia"},
    {"name": "Pneus Express", "type": "Gommista", "lat": 43.7696, "lon": 11.2558, "region": "Toscana"},
    {"name": "Carrozzeria Sud", "type": "Officina", "lat": 38.9054, "lon": 16.5873, "region": "Calabria"},
    {"name": "Battistrada Sicuro", "type": "Gommista", "lat": 39.2238, "lon": 9.1217, "region": "Sardegna"},
    {"name": "Service Rossi", "type": "Officina", "lat": 43.6158, "lon": 13.5189, "region": "Marche"},
    {"name": "Officina Adriatica", "type": "Officina", "lat": 42.4618, "lon": 14.2161, "region": "Abruzzo"},
    {"name": "Gomme & Co. Elite", "type": "Gommista", "lat": 46.0711, "lon": 13.2373, "region": "Friuli-Venezia Giulia"},
    {"name": "Meccanica Ligure", "type": "Officina", "lat": 44.4056, "lon": 8.9463, "region": "Liguria"},
    {"name": "Alpina Service", "type": "Officina", "lat": 46.0679, "lon": 11.1211, "region": "Trentino-Alto Adige"},
    {"name": "Pneus Umbria", "type": "Gommista", "lat": 43.1107, "lon": 12.3908, "region": "Umbria"},
    {"name": "Lucania Motors", "type": "Officina", "lat": 40.6333, "lon": 15.8000, "region": "Basilicata"},
    {"name": "Molise Gomme", "type": "Gommista", "lat": 41.5603, "lon": 14.6599, "region": "Molise"},
    {"name": "Garage Monte Bianco", "type": "Officina", "lat": 45.7373, "lon": 7.3201, "region": "Valle d'Aosta"}
]

router = APIRouter()
actuarial_model = ActuarialModel()
fleet_model = FleetModel()

@router.get("/api/actuarial/summary")
def get_actuarial_summary():
    return actuarial_model.generate_executive_summary(account_id=0)

@router.get("/api/actuarial/deep-dive")
def get_demographic_deep_dive():
    return actuarial_model.get_demographic_deep_dive()

@router.get("/api/actuarial/vsi")
def get_asset_risk_portfolio():
    return actuarial_model.get_asset_risk_portfolio()

@router.get("/api/fleet/map", response_class=HTMLResponse)
def get_fleet_map(view: str = 'fleet'):
    regional_kpis = fleet_model.get_regional_kpis(0)
    
    fleet_map = folium.Map(tiles='CartoDB dark_matter', zoom_control=False)
    fleet_map.fit_bounds([[36.0, 6.5], [47.1, 18.5]]) 
    
    css = "<style>.leaflet-tile-pane { filter: brightness(1.2) contrast(0.9); }</style>"
    fleet_map.get_root().header.add_child(folium.Element(css))
    
    if view == 'fleet':
        for r in regional_kpis:
            if r['center_lat'] is None or r['center_lon'] is None:
                continue
            
            html_popup = f"""
            <div style="width: 270px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 12px; border-radius: 8px;">
                <h3 style="margin: 0 0 10px 0; color: white; border-bottom: 1px solid #555; padding-bottom: 5px;">📍 {r['region_name']}</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>Tracked Vehicles:</span><span style="color: white; font-weight: bold;">{r['total_cars']:,}</span>
                </div>
                
                <div style="background-color: #1a1a1a; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                    <div style="font-size: 11px; color: #888; margin-bottom: 5px; text-transform: uppercase;">Behavioral Risk Clustering</div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; color: #ccc;">
                        <span>↳ Critical (High-G):</span><span style="color: #FF5A5A; font-weight: bold;">{r['risk_high']:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px; color: #ccc;">
                        <span>↳ Moderate:</span><span style="color: #E2B93B; font-weight: bold;">{r['risk_moderate']:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #ccc;">
                        <span>↳ Safe (Eco):</span><span style="color: #00A67E; font-weight: bold;">{r['risk_safe']:,}</span>
                    </div>
                </div>
            </div>
            """
            
            radius_size = max(8, min(45, r['total_cars'] / 35000))
            
            bubble_color = "#00A67E" 
            if r['risk_high'] > r['risk_safe']:
                bubble_color = "#FF5A5A" 
            elif r['risk_moderate'] > r['risk_safe']:
                bubble_color = "#E2B93B" 
            
            folium.CircleMarker(
                location=[r['center_lat'], r['center_lon']],
                radius=radius_size,
                popup=folium.Popup(html_popup, max_width=320),
                color=bubble_color, fill=True, fill_color=bubble_color, fill_opacity=0.6, weight=2
            ).add_to(fleet_map)
            
    elif view == 'suppliers':
        for sup in SERVICE_PROVIDERS:
            icon_color = "blue" if "Officina" in sup['type'] else "orange"
            icon_type = "wrench" if "Officina" in sup['type'] else "life-ring"
            
            html_popup = f"""
            <div style="width: 220px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 10px; border-radius: 8px; border: 1px solid {icon_color};">
                <h3 style="margin: 0 0 5px 0; color: white;">🛡️ {sup['name']}</h3>
                <div style="color: {icon_color}; font-weight: bold; margin-bottom: 10px;">{sup['type']} Convenzionata</div>
                <div style="font-size: 12px; color: #bbb;">Region: {sup['region']}</div>
            </div>
            """
            
            folium.Marker(
                location=[sup['lat'], sup['lon']],
                popup=folium.Popup(html_popup, max_width=250),
                icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
            ).add_to(fleet_map)

    return HTMLResponse(fleet_map.get_root().render())
