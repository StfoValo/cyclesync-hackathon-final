import os
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame, QLabel, QFileDialog
from PyQt6.QtGui import QPixmap
from qfluentwidgets import LineEdit, PrimaryPushButton, SubtitleLabel, BodyLabel, FluentIcon, PushButton, ComboBox

class CarModelFormWidget(QWidget):
    form_submitted = pyqtSignal(dict)
    cancel_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("CarModelFormWidget")
        self.selected_image_path = ""
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        self.card = QFrame(self)
        self.card.setFixedWidth(750) 
        self.card.setStyleSheet("QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; }")
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(25)
        
        self.title = SubtitleLabel("Vehicle Registration & Telematics Setup", self.card)
        card_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        content_layout = QHBoxLayout()
        card_layout.addLayout(content_layout)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        
        self.model_name_input = LineEdit(self.card)
        self.model_name_input.setPlaceholderText("e.g. Fiat 500e")
        form_layout.addRow(BodyLabel("Model Name:", self.card), self.model_name_input)
        
        self.plate_input = LineEdit(self.card)
        self.plate_input.setPlaceholderText("e.g. AB123CD")
        form_layout.addRow(BodyLabel("License Plate:", self.card), self.plate_input)
        
        self.car_type_combo = ComboBox(self.card)
        self.car_type_combo.addItems(["SUV", "Sedan", "Coupe", "Sportcar"])
        form_layout.addRow(BodyLabel("Chassis Type:", self.card), self.car_type_combo)
        
        self.powertrain_combo = ComboBox(self.card)
        self.powertrain_combo.addItems(["BEV", "ICE", "PHEV", "HEV"])
        form_layout.addRow(BodyLabel("Powertrain:", self.card), self.powertrain_combo)
        
        self.drivetrain_combo = ComboBox(self.card)
        self.drivetrain_combo.addItems(["RWD", "AWD", "FWD"])
        form_layout.addRow(BodyLabel("Drivetrain:", self.card), self.drivetrain_combo)
        
        content_layout.addLayout(form_layout, stretch=2)
        
        # Image Preview Section
        image_layout = QVBoxLayout()
        self.image_preview = QLabel("No Image Selected", self.card)
        self.image_preview.setFixedSize(300, 200)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("border: 2px dashed #555; border-radius: 8px; background-color: #1e1e1e;")
        image_layout.addWidget(self.image_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.btn_select_image = PrimaryPushButton(FluentIcon.PHOTO, "Upload Vehicle Photo", self.card)
        self.btn_select_image.clicked.connect(self._on_select_image)
        image_layout.addWidget(self.btn_select_image, alignment=Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addLayout(image_layout, stretch=1)
        
        self.submit_btn = PrimaryPushButton(FluentIcon.SAVE, "Register Vehicle", self.card)
        self.submit_btn.clicked.connect(self._on_submit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        self.btn_cancel = PushButton("Cancel", self.card)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.submit_btn)
        
        card_layout.addLayout(btn_layout)
        main_layout.addWidget(self.card)

    def _on_select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Car Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def reset_image(self):
        self.selected_image_path = ""
        self.image_preview.clear()
        self.image_preview.setText("No Image Selected")

    def _on_submit(self):
        data = {
            "model_name": self.model_name_input.text(),
            "plate_number": self.plate_input.text(),
            "car_type": self.car_type_combo.currentText(),
            "powertrain": self.powertrain_combo.currentText(),
            "drivetrain": self.drivetrain_combo.currentText(),
            "image_path": self.selected_image_path
        }
        self.form_submitted.emit(data)