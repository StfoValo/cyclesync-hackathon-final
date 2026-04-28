from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import (SubtitleLabel, TitleLabel, BodyLabel, 
                            ProgressRing, ProgressBar, CardWidget, CaptionLabel)

class EcoCoachWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("EcoCoachWidget")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        # --- TITLE ---
        header = SubtitleLabel("Eco-Coach & Behavioral Insights", self)
        self.layout.addWidget(header)
        self.layout.addSpacing(10)
        
        # --- TOP SECTION: The Smoothness Score ---
        score_card = CardWidget(self)
        score_layout = QHBoxLayout(score_card)
        score_layout.setContentsMargins(20, 20, 20, 20)
        
        self.score_ring = ProgressRing(self)
        self.score_ring.setFixedSize(140, 140)
        self.score_ring.setTextVisible(True)
        self.score_ring.setStrokeWidth(12)
        score_layout.addWidget(self.score_ring, alignment=Qt.AlignmentFlag.AlignCenter)
        
        score_text_layout = QVBoxLayout()
        score_text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        score_text_layout.addWidget(TitleLabel("Smoothness Score"))
        score_text_layout.addWidget(BodyLabel("Calculated using IMU G-Force telemetry and GNSS speed variations."))
        
        self.impact_label = CaptionLabel("Battery lifespan impact: Calculating...", self)
        self.impact_label.setStyleSheet("color: #00A67E; font-weight: bold; font-size: 14px;")
        score_text_layout.addWidget(self.impact_label)
        
        score_layout.addLayout(score_text_layout)
        score_layout.addStretch(1)
        self.layout.addWidget(score_card)
        
        # --- MIDDLE SECTION: Green Speed Adherence ---
        green_card = CardWidget(self)
        green_layout = QVBoxLayout(green_card)
        green_layout.setContentsMargins(20, 20, 20, 20)
        green_layout.setSpacing(10)
        
        green_layout.addWidget(TitleLabel("Green Speed Adherence"))
        green_layout.addWidget(BodyLabel("Optimal aerodynamic efficiency is achieved between 50-75 km/h. Staying in this zone exponentially reduces energy drain."))
        
        self.green_bar = ProgressBar(self)
        self.green_bar.setFixedHeight(12)
        green_layout.addWidget(self.green_bar)
        
        self.green_pct_label = BodyLabel("0% time spent in optimal zone", self)
        green_layout.addWidget(self.green_pct_label)
        self.layout.addWidget(green_card)
        
        # --- BOTTOM SECTION: IMU Harsh Events ---
        events_card = CardWidget(self)
        events_layout = QVBoxLayout(events_card)
        events_layout.setContentsMargins(20, 20, 20, 20)
        events_layout.setSpacing(15)
        
        events_layout.addWidget(TitleLabel("Harsh Event Tracker"))
        events_layout.addWidget(BodyLabel("Sudden accelerations (>0.3g) induce massive thermal stress on the battery pack and accelerate tire micro-abrasions."))
        
        # We use a horizontal layout to spread out the 3 event types
        h_layout = QHBoxLayout()
        
        self.lbl_avg = self._build_event_counter("Average\n(0.3g - 0.5g)", "#E2B93B", h_layout)
        self.lbl_hvy = self._build_event_counter("Heavy\n(0.5g - 0.8g)", "#FF9800", h_layout)
        self.lbl_ext = self._build_event_counter("Extreme\n(>0.8g)", "#FF5A5A", h_layout)
        
        events_layout.addLayout(h_layout)
        self.layout.addWidget(events_card)
        
        self.layout.addStretch(1)

    def _build_event_counter(self, title, color, parent_layout):
        container = QVBoxLayout()
        container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header = BodyLabel(title, self)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.addWidget(header)
        
        counter = TitleLabel("0", self)
        counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        counter.setStyleSheet(f"color: {color}; font-size: 36px; font-weight: bold;")
        container.addWidget(counter)
        
        parent_layout.addLayout(container)
        return counter

    def update_dashboard(self, score, green_pct, h_avg, h_hvy, h_ext, powertrain_type):
        """Called by the controller whenever new telemetry is generated."""
        
        # 1. Update Smoothness Ring
        s = int(score)
        self.score_ring.setValue(s)
        self.score_ring.setFormat(f"{s}/100")
        
        if s >= 85:
            self.score_ring.setStyleSheet("") # Default Green
            impact_text = "Extending component lifespan by +12%"
            impact_color = "#00A67E"
        elif s >= 60:
            self.score_ring.setStyleSheet("qproperty-color: #E2B93B;") # Yellow
            impact_text = "Standard component wear rate"
            impact_color = "#E2B93B"
        else:
            self.score_ring.setStyleSheet("qproperty-color: #FF5A5A;") # Red
            impact_text = "WARNING: Accelerated degradation detected"
            impact_color = "#FF5A5A"
            
        self.impact_label.setText(impact_text)
        self.impact_label.setStyleSheet(f"color: {impact_color}; font-weight: bold; font-size: 14px;")

        # 2. Update Green Speed Bar
        g = int(green_pct)
        self.green_bar.setValue(g)
        self.green_pct_label.setText(f"{g}% of recent driving spent in optimal efficiency zone")

        # 3. Update Event Counters
        self.lbl_avg.setText(str(h_avg))
        self.lbl_hvy.setText(str(h_hvy))
        self.lbl_ext.setText(str(h_ext))