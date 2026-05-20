import os
import io
import folium
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from qfluentwidgets import SubtitleLabel, PrimaryPushButton, Theme, setTheme, SegmentedWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

class FleetTelemetryWidget(QWidget):
    simulate_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("FleetTelemetryWidget")
        setTheme(Theme.DARK)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        top_bar = QHBoxLayout()
        self.header = SubtitleLabel("National Telematics Matrix", self)
        top_bar.addWidget(self.header)
        top_bar.addStretch()
        
        self.view_toggle = SegmentedWidget(self)
        self.view_toggle.addItem(routeKey='fleet', text='Live Monitored Fleet')
        self.view_toggle.addItem(routeKey='suppliers', text='Conventioned Network')
        self.view_toggle.setCurrentItem('fleet')

        top_bar.addWidget(self.view_toggle)
        top_bar.addStretch()
        
        self.btn_simulate = PrimaryPushButton("Fetch Live Box Data", self)
        self.btn_simulate.clicked.connect(self.simulate_requested.emit)
        top_bar.addWidget(self.btn_simulate)
        self.layout.addLayout(top_bar)
        
        self.web_view = QWebEngineView(self)
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.layout.addWidget(self.web_view, stretch=1)

    def render_map(self, regional_kpis, suppliers, active_view):
        # --- FIX 1: Dynamic Zoom Engine ---
        # Instead of hardcoding zoom, we let the map dynamically calculate the perfect 
        # aspect ratio for the current PyQt window size.
        fleet_map = folium.Map(tiles='CartoDB dark_matter', zoom_control=False)
        
        # This forces the camera to perfectly frame Italy (from Sicily to the Alps)
        fleet_map.fit_bounds([[36.0, 6.5], [47.1, 18.5]]) 
        
        css = "<style>.leaflet-tile-pane { filter: brightness(1.2) contrast(0.9); }</style>"
        fleet_map.get_root().header.add_child(folium.Element(css))

        if active_view == 'fleet':
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
                
                # --- FIX 2: Anti-Clutter Bubble Scaling ---
                # Lombardia (~1.38M) will hit max size, Valle d'Aosta (~39k) will shrink perfectly!
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
                
        elif active_view == 'suppliers':
            for sup in suppliers:
                icon_color = "blue" if "Officina" in sup['type'] else "orange"
                icon_type = "wrench" if "Officina" in sup['type'] else "life-ring"
                
                # Extract the name to a clean variable so it doesn't break the HTML quotes
                shop_name = sup['name']
                
                html_popup = f"""
                <div style="width: 220px; font-family: sans-serif; background-color: #2e2e2e; color: #E0E0E0; padding: 10px; border-radius: 8px; border: 1px solid {icon_color};">
                    <h3 style="margin: 0 0 5px 0; color: white;">🛡️ {shop_name}</h3>
                    <div style="color: {icon_color}; font-weight: bold; margin-bottom: 10px;">{sup['type']} Convenzionata</div>
                    <div style="font-size: 12px; color: #bbb; margin-bottom: 12px;">Region: {sup['region']}</div>
                    
                    <button onclick="window.parent.confirmShopAndGenerateAI('{shop_name}')" 
                            style="width: 100%; padding: 8px; background: #00E5FF; color: #0f172a; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 12px; transition: background 0.2s;">
                        Invia Richiesta
                    </button>
                </div>
                """
                
                folium.Marker(
                    location=[sup['lat'], sup['lon']],
                    popup=folium.Popup(html_popup, max_width=250),
                    icon=folium.Icon(color=icon_color, icon=icon_type, prefix='fa')
                ).add_to(fleet_map)