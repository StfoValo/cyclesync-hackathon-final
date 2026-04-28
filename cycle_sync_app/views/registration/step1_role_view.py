from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from qfluentwidgets import SubtitleLabel, PrimaryPushButton

class Step1RoleView(QWidget):
    role_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = SubtitleLabel("Welcome to the Digital Mobility Ecosystem", self)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        
        button_layout = QHBoxLayout()
        
        # --- THE NEW UNIPOL ROLES ---
        self.btn_driver = PrimaryPushButton("🚗 Vehicle Owner", self)
        self.btn_insurer = PrimaryPushButton("🛡️ Insurance Actuary ", self)
        
        self.btn_driver.clicked.connect(lambda: self.role_selected.emit("DRIVER"))
        self.btn_insurer.clicked.connect(lambda: self.role_selected.emit("INSURER"))
        
        button_layout.addWidget(self.btn_driver)
        button_layout.addWidget(self.btn_insurer)
        
        layout.addLayout(button_layout)