from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QFrame
from qfluentwidgets import SubtitleLabel, PrimaryPushButton, BodyLabel, ComboBox, Theme, setTheme, FluentIcon

class AIStreamWorker(QThread):
    """Safely runs the AI generator in the background so the UI doesn't freeze."""
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, stream_generator):
        super().__init__()
        self.stream_generator = stream_generator
        
    def run(self):
        try:
            for chunk in self.stream_generator:
                self.chunk_received.emit(chunk)
        except Exception as e:
            self.chunk_received.emit(f"\n\n**[Stream Interrupted]** {str(e)}")
        finally:
            self.finished.emit()

class AiStrategyWidget(QWidget):
    # This signal tells the controller: "Hey, the user wants to analyze this region!"
    analyze_requested = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("AiStrategyWidget")
        setTheme(Theme.DARK)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        self.title = SubtitleLabel("Enterprise AI Strategy & Routing Directive", self)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # --- CONTROLS SECTION ---
        control_frame = QFrame(self)
        control_frame.setStyleSheet("QFrame { background-color: #272727; border-radius: 10px; border: 1px solid #3a3a3a; }")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(20, 20, 20, 20)
        
        control_layout.addWidget(BodyLabel("📍 Select Target Region:", self))
        
        self.region_selector = ComboBox(self)
        # Pre-populate the Italian Regions
        regions = ["Lombardia", "Lazio", "Campania", "Sicilia", "Veneto", "Emilia-Romagna", 
                   "Piemonte", "Puglia", "Toscana", "Calabria", "Sardegna", "Liguria", 
                   "Marche", "Abruzzo", "Friuli-Venezia Giulia", "Trentino-Alto Adige", 
                   "Umbria", "Basilicata", "Molise", "Valle d'Aosta"]
        self.region_selector.addItems(sorted(regions))
        control_layout.addWidget(self.region_selector)
        
        control_layout.addStretch()
        
        # The Big Action Button
        self.btn_analyze = PrimaryPushButton(FluentIcon.ROBOT, "Generate Intervention Strategy", self)
        self.btn_analyze.setStyleSheet("background: #5A32FA; border-color: #5A32FA;") # Deep AI Purple
        self.btn_analyze.clicked.connect(self._on_analyze_clicked)
        control_layout.addWidget(self.btn_analyze)
        
        main_layout.addWidget(control_frame)

        # --- THE AI TERMINAL ---
        self.ai_terminal = QTextBrowser(self)
        self.ai_terminal.setStyleSheet("""
            QTextBrowser {
                background-color: #121212;
                color: #00FF41; /* Classic Terminal Green */
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                border-radius: 10px;
                border: 1px solid #3a3a3a;
                padding: 15px;
            }
        """)
        self.ai_terminal.setOpenExternalLinks(True)
        self.ai_terminal.setHtml("<b style='color: #aaaaaa;'>[SYSTEM READY]</b> Awaiting actuarial input...<br>")
        main_layout.addWidget(self.ai_terminal, stretch=1)

    def _on_analyze_clicked(self):
        """Disables the button and tells the controller to fetch the data."""
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Orchestrating Network...")
        selected_region = self.region_selector.currentText()
        self.analyze_requested.emit(selected_region)

    def prepare_ai_stream(self, region):
        """Clears the terminal and preps it for incoming text."""
        self.ai_terminal.clear()
        self.ai_terminal.insertHtml(f"<b style='color: #00A67E;'>[INIT]</b> Ingesting VSI Telemetry and Local Supply Chain for <b>{region}</b>...<br><br>")

    def stream_ai_response(self, stream_generator):
        """Spawns the worker thread to safely stream text into the UI."""
        self.worker = AIStreamWorker(stream_generator)
        self.worker.chunk_received.connect(self._append_chunk)
        self.worker.finished.connect(self._on_stream_finished)
        self.worker.start()

    def _append_chunk(self, chunk):
        """Appends text and auto-scrolls to the bottom."""
        # Convert markdown-style headers simply for the terminal view
        clean_chunk = chunk.replace('###', '\n\n>>').replace('**', '')
        self.ai_terminal.insertPlainText(clean_chunk)
        
        # Auto-scroll
        scrollbar = self.ai_terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_stream_finished(self):
        """Re-enables the UI when the AI is done."""
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("Generate Intervention Strategy")
        self.ai_terminal.insertHtml("<br><br><b style='color: #00A67E;'>[PROCESS COMPLETE]</b> Directives ready for dispatch.")
