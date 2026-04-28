from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QStackedWidget
from qfluentwidgets import SubtitleLabel, TitleLabel, BodyLabel, CaptionLabel, ProgressBar, SmoothScrollArea, PrimaryPushButton, FluentIcon

# --- IMPORT YOUR OLD FORM ---
from views.insurer_widgets.car_model_form_widget import CarModelFormWidget

class GarageWidget(QWidget):
    trip_simulated = pyqtSignal(str)
    vehicle_added = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("GarageWidget")
        
        # --- NEW: Stacked Widget Base ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget)
        
        # --- INDEX 0: The Garage Page ---
        self.garage_page = QWidget()
        self.garage_layout = QVBoxLayout(self.garage_page)
        self.garage_layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        self.title = SubtitleLabel("My Garage & Vehicle Identity", self)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        
        # The new "Buy/Register Car" button!
        self.btn_add_car = PrimaryPushButton(FluentIcon.ADD, "Register New Vehicle", self)
        header_layout.addWidget(self.btn_add_car)
        self.garage_layout.addLayout(header_layout)
        self.garage_layout.addSpacing(20)
        
        self.scroll_area = SmoothScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container) 
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.cards_container)
        self.garage_layout.addWidget(self.scroll_area)
        
        # --- INDEX 1: The Registration Form Page ---
        self.form_page = CarModelFormWidget(self)
        # Rename the form title to fit the new context
        self.form_page.title.setText("Vehicle Registration & Telematics Setup")
        
        # Add pages to stack
        self.stacked_widget.addWidget(self.garage_page) # Index 0
        self.stacked_widget.addWidget(self.form_page)   # Index 1

    def render_vehicle_card(self, vin, model_name, car_type, image_path, odometer, driving_score):
        card = QFrame(self.cards_container)
        card.setStyleSheet("QFrame { background-color: #272727; border-radius: 15px; border: 1px solid #3a3a3a; }")
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(30)
        
        # --- Image Section ---
        image_label = QLabel(card)
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(pixmap)
        else:
            image_label.setText("No Image")
            image_label.setStyleSheet("color: #aaa; border: 2px dashed #555; border-radius: 8px;")
            
        image_label.setFixedSize(300, 200)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(image_label)
        
        # --- Details Section (OEM Blueprint Data) ---
        details_layout = QVBoxLayout()
        details_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        details_layout.setSpacing(5)
        
        title = TitleLabel(model_name, card)
        title.setStyleSheet("color: white;")
        type_label = BodyLabel(f"Category: {car_type.upper()}", card)
        vin_label = CaptionLabel(f"Digital Passport VIN: {vin}", card)
        vin_label.setStyleSheet("color: #888;")
        
        details_layout.addWidget(title)
        details_layout.addWidget(type_label)
        details_layout.addWidget(vin_label)
        details_layout.addSpacing(20)
        
        # --- Telemetry Section (Live Sensor Data) ---
        telemetry_label = SubtitleLabel("Live Telemetry", card)
        telemetry_label.setStyleSheet("color: #00A67E;")
        
        telemetry_header_layout = QHBoxLayout()
        telemetry_header_layout.addWidget(telemetry_label)
        
        btn_simulate = PrimaryPushButton(FluentIcon.CAR, "Simulate Trip", card)
        btn_simulate.clicked.connect(lambda checked, v=vin: self.trip_simulated.emit(v))
        telemetry_header_layout.addWidget(btn_simulate)
        telemetry_header_layout.addStretch()
        
        details_layout.addLayout(telemetry_header_layout)
        
        odo_val = odometer if odometer is not None else 0
        score_val = int(driving_score) if driving_score is not None else 100
        
        details_layout.addWidget(BodyLabel(f"Total Distance: {odo_val:,} km", card))
        details_layout.addWidget(BodyLabel(f"Eco-Driving Score: {score_val}/100", card))
        
        # A cool visual progress bar for the driving score
        score_bar = ProgressBar(card)
        score_bar.setFixedSize(200, 10)
        score_bar.setValue(score_val)
        details_layout.addWidget(score_bar)
        
        card_layout.addLayout(details_layout)
        card_layout.addStretch()
        
        self.cards_layout.addWidget(card)

    def show_empty_message(self):
        empty_label = BodyLabel("No vehicles registered to this account.", self.cards_container)
        self.cards_layout.addWidget(empty_label)

    def clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()