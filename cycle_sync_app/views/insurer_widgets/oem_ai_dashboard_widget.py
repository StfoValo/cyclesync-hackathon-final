import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
from qfluentwidgets import SubtitleLabel, TitleLabel, BodyLabel, Theme, setTheme
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

class OemAiDashboardWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("PredictiveAssetDashboard")
        setTheme(Theme.DARK)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        self.title = SubtitleLabel("Predictive Asset & Hardware Risk (VSI)", self)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- KPI CARDS ---
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        self.kpi_vsi = self._create_kpi_card("Fleet Average VSI Score", "0.0/100", "🛡️")
        self.kpi_critical = self._create_kpi_card("Vehicles in Critical State", "0", "⚠️")
        self.kpi_cost = self._create_kpi_card("Projected Hardware Claims", "€0", "💶")
        kpi_layout.addWidget(self.kpi_vsi)
        kpi_layout.addWidget(self.kpi_critical)
        kpi_layout.addWidget(self.kpi_cost)
        main_layout.addLayout(kpi_layout)

        # --- SCROLLING CHART VIEW ---
        self.chart_view = QWebEngineView(self)
        self.chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_view.setStyleSheet("background-color: transparent; border-radius: 12px;")
        main_layout.addWidget(self.chart_view, stretch=1)

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

    def populate_dashboard(self, portfolio_data):
        metrics = portfolio_data['metrics']
        
        vsi_val = metrics['avg_vsi_score']
        vsi_lbl = self.kpi_vsi.findChild(TitleLabel, "value_label")
        vsi_lbl.setText(f"{vsi_val:.1f}/100")
        vsi_lbl.setStyleSheet(f"color: {'#00A67E' if vsi_val > 75 else '#E2B93B' if vsi_val > 60 else '#FF5A5A'}; border: none;")
        
        self.kpi_critical.findChild(TitleLabel, "value_label").setText(f"{int(metrics['total_critical_assets']):,}")
        self.kpi_cost.findChild(TitleLabel, "value_label").setText(f"€{metrics['projected_hardware_claims_eur']:,.2f}")
        
        self._render_scrolling_charts(portfolio_data)

    def _render_scrolling_charts(self, p):
        # --- FIX 1: Filter out any manual test cars/dummy regions ---
        clean_regional = [r for r in p["regional"] if "Unipol" not in r["region"] and r["region"].strip() != ""]
        
        # Extract Regional Data using the cleaned array
        regions = [r["region"] for r in clean_regional]
        
        vsi_s, vsi_w, vsi_c = [r["vsi"][0] for r in clean_regional], [r["vsi"][1] for r in clean_regional], [r["vsi"][2] for r in clean_regional]
        brk_s, brk_w, brk_c = [r["brakes"][0] for r in clean_regional], [r["brakes"][1] for r in clean_regional], [r["brakes"][2] for r in clean_regional]
        tir_s, tir_w, tir_c = [r["tires"][0] for r in clean_regional], [r["tires"][1] for r in clean_regional], [r["tires"][2] for r in clean_regional]
        
        # Extract Global Data
        g_vsi = list(p["global"]["overall_vsi"].values())
        g_brk = list(p["global"]["brakes"].values())
        g_tir = list(p["global"]["tires"].values())

        html = f"""
        <!DOCTYPE html><html><head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
        <style>
            body {{ margin: 0; padding: 0 10px; background-color: #1e1e1e; font-family: sans-serif; overflow-y: auto; overflow-x: hidden; }}
            .dashboard-container {{ display: flex; flex-direction: column; gap: 20px; padding-bottom: 30px; }}
            .chart-card {{ background: #272727; border-radius: 10px; padding: 15px; border: 1px solid #3a3a3a; display: flex; flex-direction: column; }}
            .tall-card {{ height: 500px; }} 
            .donut-row {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; height: 300px; }}
            .chart-wrapper {{ position: relative; flex: 1 1 auto; width: 100%; height: 0; }}
            h3 {{ color: #aaa; text-align: center; font-size: 16px; margin: 0 0 15px 0; border-bottom: 1px solid #444; padding-bottom: 10px; }}
            ::-webkit-scrollbar {{ width: 8px; }} ::-webkit-scrollbar-track {{ background: #1e1e1e; }} ::-webkit-scrollbar-thumb {{ background: #555; border-radius: 4px; }}
        </style></head><body>
        
        <div class="dashboard-container">
            <div class="chart-card tall-card">
                <h3>Regional Fleet Safety Index (VSI) Breakdown</h3>
                <div class="chart-wrapper"><canvas id="vsiRegionChart"></canvas></div>
            </div>
            
            <div class="chart-card tall-card">
                <h3>Regional Brake Pad Degradation Matrix</h3>
                <div class="chart-wrapper"><canvas id="brakeRegionChart"></canvas></div>
            </div>

            <div class="chart-card tall-card">
                <h3>Regional Tire Tread Wear Analytics</h3>
                <div class="chart-wrapper"><canvas id="tireRegionChart"></canvas></div>
            </div>

            <div class="donut-row">
                <div class="chart-card"><h3>Global VSI</h3><div class="chart-wrapper"><canvas id="vsiGlobalChart"></canvas></div></div>
                <div class="chart-card"><h3>Global Brakes</h3><div class="chart-wrapper"><canvas id="brakeGlobalChart"></canvas></div></div>
                <div class="chart-card"><h3>Global Tires</h3><div class="chart-wrapper"><canvas id="tireGlobalChart"></canvas></div></div>
            </div>
        </div>

        <script>
            // Register the DataLabels plugin globally
            Chart.register(ChartDataLabels);
            
            Chart.defaults.color = '#aaa';
            Chart.defaults.borderColor = '#333'; 
            
            const commonStackOptions = {{
                responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: {{ 
                    legend: {{ position: 'bottom', labels: {{ color: '#fff' }} }},
                    // Turn OFF datalabels for the bar charts so they don't get cluttered with numbers!
                    datalabels: {{ display: false }} 
                }},
                scales: {{ x: {{ stacked: true, grid: {{ color: '#333' }} }}, y: {{ stacked: true, grid: {{ display: false }} }} }}
            }};

            new Chart(document.getElementById('vsiRegionChart'), {{ type: 'bar', data: {{ labels: {json.dumps(regions)}, datasets: [
                {{ label: 'Safe', data: {json.dumps(vsi_s)}, backgroundColor: '#00A67E' }},
                {{ label: 'Warning', data: {json.dumps(vsi_w)}, backgroundColor: '#E2B93B' }},
                {{ label: 'Critical', data: {json.dumps(vsi_c)}, backgroundColor: '#FF5A5A' }} ]}}, options: commonStackOptions }});
                
            new Chart(document.getElementById('brakeRegionChart'), {{ type: 'bar', data: {{ labels: {json.dumps(regions)}, datasets: [
                {{ label: 'Safe (>6mm)', data: {json.dumps(brk_s)}, backgroundColor: '#00A67E' }},
                {{ label: 'Warning (3-6mm)', data: {json.dumps(brk_w)}, backgroundColor: '#E2B93B' }},
                {{ label: 'Critical (<3mm)', data: {json.dumps(brk_c)}, backgroundColor: '#FF5A5A' }} ]}}, options: commonStackOptions }});

            new Chart(document.getElementById('tireRegionChart'), {{ type: 'bar', data: {{ labels: {json.dumps(regions)}, datasets: [
                {{ label: 'Safe (>4mm)', data: {json.dumps(tir_s)}, backgroundColor: '#00A67E' }},
                {{ label: 'Warning (2-4mm)', data: {json.dumps(tir_w)}, backgroundColor: '#E2B93B' }},
                {{ label: 'Critical (<2mm)', data: {json.dumps(tir_c)}, backgroundColor: '#FF5A5A' }} ]}}, options: commonStackOptions }});

            // --- FIX 2: Activate and format DataLabels for the Doughnut charts ---
            const dOptions = {{ 
                responsive: true, 
                maintainAspectRatio: false, 
                cutout: '65%', 
                plugins: {{ 
                    legend: {{ position: 'bottom' }},
                    datalabels: {{
                        color: '#fff',
                        font: {{ weight: 'bold', size: 12 }},
                        formatter: (value, ctx) => {{
                            let sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            if (sum === 0) return '';
                            let pct = (value * 100 / sum).toFixed(1) + '%';
                            // Hide the label if the segment is too small (<5%) to prevent text overlap
                            return (value * 100 / sum) > 5 ? pct : '';
                        }}
                    }}
                }} 
            }};
            
            new Chart(document.getElementById('vsiGlobalChart'), {{ type: 'doughnut', data: {{ labels: ['Safe', 'Warning', 'Critical'], datasets: [{{ data: {json.dumps(g_vsi)}, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }}]}}, options: dOptions }});
            new Chart(document.getElementById('brakeGlobalChart'), {{ type: 'doughnut', data: {{ labels: ['Safe', 'Warning', 'Critical'], datasets: [{{ data: {json.dumps(g_brk)}, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }}]}}, options: dOptions }});
            new Chart(document.getElementById('tireGlobalChart'), {{ type: 'doughnut', data: {{ labels: ['Safe', 'Warning', 'Critical'], datasets: [{{ data: {json.dumps(g_tir)}, backgroundColor: ['#00A67E', '#E2B93B', '#FF5A5A'], borderWidth: 0 }}]}}, options: dOptions }});
        </script></body></html>"""
        self.chart_view.setHtml(html)