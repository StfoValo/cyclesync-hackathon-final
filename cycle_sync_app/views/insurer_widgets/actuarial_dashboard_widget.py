import json
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
from qfluentwidgets import SubtitleLabel, BodyLabel, TitleLabel, Theme, setTheme, SegmentedWidget, PrimaryPushButton, FluentIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

class ActuarialDashboardWidget(QWidget):
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ActuarialDashboardWidget")
        setTheme(Theme.DARK)
        
        self.regional_data = None
        self.demographic_data = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- TITLE, TABS & AI BUTTON ---
        header_layout = QHBoxLayout()
        self.title = SubtitleLabel("Actuarial Risk & Financial Dashboard", self)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        
        # The Tab Switcher
        self.view_toggle = SegmentedWidget(self)
        self.view_toggle.addItem(routeKey='overview', text='Regional Overview')
        self.view_toggle.addItem(routeKey='demographics', text='Demographic Deep Dive')
        self.view_toggle.setCurrentItem('overview')
        self.view_toggle.currentItemChanged.connect(self._switch_chart_view)
        header_layout.addWidget(self.view_toggle)
        header_layout.addStretch()
        
        # The Future AI Button
        self.btn_ai_assist = PrimaryPushButton(FluentIcon.ROBOT, "Ask AI Actuary", self)
        self.btn_ai_assist.setStyleSheet("background: #5A32FA; border-color: #5A32FA;") # Deep Purple AI feel
        header_layout.addWidget(self.btn_ai_assist)
        
        main_layout.addLayout(header_layout)

        self.shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut.activated.connect(self.refresh_requested.emit)

        # --- TOP KPI CARDS ---
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        self.kpi_fleet = self._create_kpi_card("Total Active Policies", "0", "📄")
        self.kpi_premium = self._create_kpi_card("Avg. Annual Premium", "€0.00", "💰")
        self.kpi_discount = self._create_kpi_card("Telematics Discount", "0.0%", "📉")
        self.kpi_claims = self._create_kpi_card("Claims Reduction", "0.0%", "🛡️")
        kpi_layout.addWidget(self.kpi_fleet)
        kpi_layout.addWidget(self.kpi_premium)
        kpi_layout.addWidget(self.kpi_discount)
        kpi_layout.addWidget(self.kpi_claims)
        main_layout.addLayout(kpi_layout)

        # --- DYNAMIC CHART VIEW ---
        self.chart_view = QWebEngineView(self)
        self.chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_view.setStyleSheet("background-color: transparent; border-radius: 12px;")
        main_layout.addWidget(self.chart_view, stretch=1)
        self.chart_view.setHtml("<html><body style='background-color: #1e1e1e;'></body></html>")

    def _create_kpi_card(self, title_text, value_text, icon):
        card = QFrame(self)
        card.setStyleSheet("QFrame { background-color: #272727; border-radius: 10px; border: 1px solid #3a3a3a; }")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        header = BodyLabel(f"{icon} {title_text}", card)
        header.setStyleSheet("color: #aaaaaa; font-weight: bold; border: none;")
        value = TitleLabel(value_text, card)
        value.setStyleSheet("color: #ffffff; border: none;")
        value.setObjectName("value_label")
        layout.addWidget(header)
        layout.addWidget(value)
        return card

    def populate_dashboard(self, regional_payload, demographic_payload):
        self.regional_data = regional_payload
        self.demographic_data = demographic_payload
        
        kpis = regional_payload['kpis']
        self.kpi_fleet.findChild(TitleLabel, "value_label").setText(f"{int(kpis['total_monitored_fleet']):,}")
        self.kpi_premium.findChild(TitleLabel, "value_label").setText(f"€{kpis['average_premium_eur']:,.2f}")
        
        discount_str = f"{kpis['average_discount_pct']:.1f}%"
        lbl_discount = self.kpi_discount.findChild(TitleLabel, "value_label")
        lbl_discount.setText(discount_str)
        lbl_discount.setStyleSheet("color: #00A67E; border: none;" if kpis['average_discount_pct'] < 0 else "color: #FF5A5A; border: none;")
        self.kpi_claims.findChild(TitleLabel, "value_label").setText(f"{kpis['claims_reduction_pct']:.1f}%")

        self._switch_chart_view()

    def _switch_chart_view(self):
        if not self.regional_data or not self.demographic_data: return
        
        current_tab = self.view_toggle.currentItem().text()
        
        if "Regional" in current_tab:
            self._render_regional_chart()
        else:
            self._render_demographic_grid()

    def _render_regional_chart(self):
        regions = [r['region'] for r in self.regional_data['regional_breakdown']]
        projected = [r['projected_accidents'] for r in self.regional_data['regional_breakdown']]
        registered = [r['registered_claims'] for r in self.regional_data['regional_breakdown']]
        
        html = f"""
        <!DOCTYPE html><html><head><script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>body {{ margin: 0; padding: 10px; background-color: #1e1e1e; font-family: sans-serif; height: 90vh; }}
        .chartWrapper {{ width: 100%; height: 100%; overflow-x: auto; overflow-y: hidden; }}
        .chartAreaWrapper {{ min-width: 1400px; height: 100%; }}
        ::-webkit-scrollbar {{ height: 8px; }} ::-webkit-scrollbar-track {{ background: #2a2a2a; }} ::-webkit-scrollbar-thumb {{ background: #555; }}
        </style></head><body>
        <div class="chartWrapper"><div class="chartAreaWrapper"><canvas id="riskChart"></canvas></div></div>
        <script>
            new Chart(document.getElementById('riskChart').getContext('2d'), {{
                type: 'bar',
                data: {{ labels: {json.dumps(regions)}, datasets: [
                    {{ label: 'Registered Claims (Baseline)', data: {json.dumps(registered)}, backgroundColor: 'rgba(120, 120, 120, 0.6)' }},
                    {{ label: 'Projected Claims (Telematics)', data: {json.dumps(projected)}, backgroundColor: 'rgba(226, 185, 59, 0.9)' }}
                ]}},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#fff' }} }} }},
                scales: {{ y: {{ grid: {{ color: '#333' }}, ticks: {{ color: '#aaa' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ color: '#aaa' }} }} }} }}
            }});
        </script></body></html>"""
        self.chart_view.setHtml(html)

    def _render_demographic_grid(self):
        d = self.demographic_data
        
        html = f"""
        <!DOCTYPE html><html><head><script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            /* --- FIX: Enabled vertical scrolling so we can stack large charts cleanly --- */
            body {{ margin: 0; padding: 15px; background-color: #1e1e1e; font-family: sans-serif; box-sizing: border-box; overflow-y: auto; overflow-x: hidden; }}
            
            .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding-bottom: 30px; }}
            .card {{ background: #272727; border-radius: 10px; padding: 15px; border: 1px solid #3a3a3a; display: flex; flex-direction: column; height: 320px; }}
            
            /* --- FIX: The new full-width stacked card --- */
            .wide-card {{ grid-column: span 2; height: 350px; }}
            
            h3 {{ color: #aaa; text-align: center; font-size: 14px; margin: 0 0 10px 0; flex: 0 0 auto; }}
            .chart-wrapper {{ position: relative; flex: 1 1 auto; width: 100%; height: 0; }}
            
            ::-webkit-scrollbar {{ width: 8px; }} ::-webkit-scrollbar-track {{ background: #1e1e1e; }} ::-webkit-scrollbar-thumb {{ background: #555; border-radius: 4px; }}
        </style></head><body>
        <div class="grid-container">
            <div class="card">
                <h3>Claims by Driver Age Group</h3>
                <div class="chart-wrapper"><canvas id="ageChart"></canvas></div>
            </div>
            <div class="card">
                <h3>Claims by Gender</h3>
                <div class="chart-wrapper"><canvas id="genderChart"></canvas></div>
            </div>
            <div class="card">
                <h3>Claims by Vehicle Category</h3>
                <div class="chart-wrapper"><canvas id="vehicleChart"></canvas></div>
            </div>
            <div class="card">
                <h3>Claims by Behavioral Risk Segment</h3>
                <div class="chart-wrapper"><canvas id="behaviorChart"></canvas></div>
            </div>
            
            <div class="card wide-card">
                <h3>Claims by Vehicle Age (Italian RCA Brackets)</h3>
                <div class="chart-wrapper"><canvas id="vehicleAgeChart"></canvas></div>
            </div>
        </div>
        <script>
            Chart.defaults.color = '#aaa';
            Chart.defaults.borderColor = '#333'; 
            
            new Chart(document.getElementById('ageChart'), {{
                type: 'bar',
                data: {{ labels: {json.dumps(list(d["age_groups"].keys()))}, datasets: [{{ label: 'Projected Claims', data: {json.dumps(list(d["age_groups"].values()))}, backgroundColor: '#4CAF50' }}]}},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
            }});

            new Chart(document.getElementById('genderChart'), {{
                type: 'doughnut',
                data: {{ labels: {json.dumps(list(d["genders"].keys()))}, datasets: [{{ data: {json.dumps(list(d["genders"].values()))}, backgroundColor: ['#2196F3', '#E91E63'], borderWidth: 0 }}]}},
                options: {{ responsive: true, maintainAspectRatio: false, cutout: '70%' }}
            }});

            new Chart(document.getElementById('vehicleChart'), {{
                type: 'bar',
                data: {{ labels: {json.dumps(list(d["vehicle_types"].keys()))}, datasets: [{{ label: 'Projected Claims', data: {json.dumps(list(d["vehicle_types"].values()))}, backgroundColor: '#FF9800' }}]}},
                options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
            }});

            new Chart(document.getElementById('behaviorChart'), {{
                type: 'bar',
                data: {{ labels: {json.dumps(list(d["behaviors"].keys()))}, datasets: [{{ label: 'Projected Claims', data: {json.dumps(list(d["behaviors"].values()))}, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'] }}]}},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
            }});
            
            // --- FIX: Render the new Vehicle Age RCA Chart ---
            new Chart(document.getElementById('vehicleAgeChart'), {{
                type: 'bar',
                data: {{ labels: {json.dumps(list(d["vehicle_ages"].keys()))}, datasets: [{{ label: 'Projected Claims', data: {json.dumps(list(d["vehicle_ages"].values()))}, backgroundColor: '#9C27B0' }}]}},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
            }});
        </script></body></html>"""
        self.chart_view.setHtml(html)