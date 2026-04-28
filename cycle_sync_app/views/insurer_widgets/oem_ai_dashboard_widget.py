import pyqtgraph as pg
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QTextBrowser, QStackedWidget
from qfluentwidgets import SubtitleLabel, PrimaryPushButton, TitleLabel, BodyLabel, SegmentedWidget
from PyQt6.QtGui import QFont

class AIStreamWorker(QThread):
    chunk_received = pyqtSignal(str)
    def __init__(self, stream_generator):
        super().__init__()
        self.stream_generator = stream_generator
    def run(self):
        try:
            for chunk in self.stream_generator:
                self.chunk_received.emit(chunk)
        except Exception as e:
            self.chunk_received.emit(f"\n\n**[Stream Interrupted]** {str(e)}")

class OemAiDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("OemAiDashboardWidget")
        
        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#aaaaaa')
        pg.setConfigOptions(antialias=True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        
        # --- TOP NAVIGATION (TABS) ---
        nav_layout = QHBoxLayout()
        self.tabs = SegmentedWidget(self)
        nav_layout.addWidget(self.tabs, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(nav_layout)
        
        # The Stacked Widget holds the content for the tabs
        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget)
        
        # Initialize the two pages
        self._build_data_tab()
        self._build_ai_tab()
        
        # Wire the tabs
        self.tabs.addItem(routeKey='data', text='Fleet Data Visualization', onClick=lambda: self.stacked_widget.setCurrentIndex(0))
        self.tabs.addItem(routeKey='ai', text='AI Strategy Directive', onClick=lambda: self.stacked_widget.setCurrentIndex(1))
        
        self.worker = None

    def _build_data_tab(self):
        """Builds the first tab containing the Stats and Histogram."""
        self.data_page = QWidget()
        data_layout = QHBoxLayout(self.data_page)
        data_layout.setContentsMargins(0, 10, 0, 0)
        data_layout.setSpacing(20)
        
        # 1. Stats Column
        stats_col = QVBoxLayout()
        self.total_bev_label = TitleLabel("0", self.data_page)
        self.total_bev_label.setStyleSheet("color: #4CAF50;")
        self.risk_lithium_label = TitleLabel("0.0 Tons", self.data_page)
        self.risk_lithium_label.setStyleSheet("color: #FF9800;")
        self.critical_batteries_label = TitleLabel("0", self.data_page)
        self.critical_batteries_label.setStyleSheet("color: #FF5A5A;")
        
        stats_col.addWidget(BodyLabel("Total Tracked BEVs", self.data_page))
        stats_col.addWidget(self.total_bev_label)
        stats_col.addSpacing(15)
        stats_col.addWidget(BodyLabel("At-Risk Lithium (0-12 Mo)", self.data_page))
        stats_col.addWidget(self.risk_lithium_label)
        stats_col.addSpacing(15)
        stats_col.addWidget(BodyLabel("Critical EOL Batteries", self.data_page))
        stats_col.addWidget(self.critical_batteries_label)
        stats_col.addStretch()
        
        stats_card = QFrame(self.data_page)
        stats_card.setFixedWidth(250)
        stats_card.setStyleSheet("QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; padding: 20px; }")
        stats_card.setLayout(stats_col)
        data_layout.addWidget(stats_card)
        
        # 2. Grouped Histogram Column
        self.plot_card = QFrame(self.data_page)
        self.plot_card.setStyleSheet("QFrame { background-color: #272727; border-radius: 12px; border: 1px solid #3a3a3a; padding: 10px; }")
        p_layout = QVBoxLayout(self.plot_card)
        p_layout.addWidget(SubtitleLabel("Critical End-of-Life Batteries by Region", self.plot_card))
        
        self.graph = pg.PlotWidget()
        self.graph.showGrid(y=True, alpha=0.15)
        self.graph.setLabel('left', '# of Vehicles')
        
        # Enable Legend
        self.graph.addLegend(offset=(10, 10))
        
        # Create TWO bar graph items for the grouped effect
        self.bar_0_3 = pg.BarGraphItem(x=[], height=[], width=0.3, brush='#2196F3', name="0-3 Months EOL")
        self.bar_3_6 = pg.BarGraphItem(x=[], height=[], width=0.3, brush='#F44336', name="3-6 Months EOL")
        
        self.graph.addItem(self.bar_0_3)
        self.graph.addItem(self.bar_3_6)
        
        p_layout.addWidget(self.graph)
        data_layout.addWidget(self.plot_card, stretch=1)
        
        self.stacked_widget.addWidget(self.data_page)

    def _build_ai_tab(self):
        """Builds the second tab containing the AI Analysis."""
        self.ai_page = QWidget()
        ai_layout = QVBoxLayout(self.ai_page)
        ai_layout.setContentsMargins(0, 10, 0, 0)
        ai_layout.setSpacing(15)
        
        self.btn_request_ai_analysis = PrimaryPushButton("Generate Supply Chain Strategy", self.ai_page)
        self.btn_request_ai_analysis.setStyleSheet("PrimaryPushButton { background: #00A67E; font-weight: bold; padding: 12px; }")
        ai_layout.addWidget(self.btn_request_ai_analysis)
        
        self.ai_text_display = QTextBrowser(self.ai_page)
        self.ai_text_display.setStyleSheet("""
            QTextBrowser {
                background-color: #181818; color: #e0e0e0;
                border-radius: 8px; border: 1px inset #333;
                padding: 20px; font-size: 15px; line-height: 1.6;
            }
        """)
        self.ai_text_display.setHtml("<p style='color: #888;'>Ready to analyze fleet payload...</p>")
        ai_layout.addWidget(self.ai_text_display)
        
        self.stacked_widget.addWidget(self.ai_page)

    def populate_dashboard(self, total_bevs, lithium_tons, critical_count, regions, eol_0_3, eol_3_6):
        """Updates the top stats and draws the grouped histogram."""
        self.total_bev_label.setText(f"{total_bevs:,}")
        self.risk_lithium_label.setText(f"{lithium_tons:,.1f} Tons")
        self.critical_batteries_label.setText(f"{critical_count:,}")
        
        # Mathematical offset to create grouped bars!
        x_base = list(range(1, len(regions) + 1))
        x_0_3 = [x - 0.15 for x in x_base]
        x_3_6 = [x + 0.15 for x in x_base]
        
        # Update both bars
        self.bar_0_3.setOpts(x=x_0_3, height=eol_0_3)
        self.bar_3_6.setOpts(x=x_3_6, height=eol_3_6)
        
        # --- FIX: EXACT X-AXIS LABEL RENDERING ---
        ticks = [[(x, str(name)) for x, name in zip(x_base, regions)]]
        bottom_axis = self.graph.getAxis('bottom')
        bottom_axis.setTicks(ticks)
        
        # 1. Shrink the font size slightly
        tick_font = QFont()
        tick_font.setPixelSize(10)
        bottom_axis.setTickFont(tick_font)
        
        # 2. Force the axis to allocate enough vertical height for our \n line breaks
        bottom_axis.setHeight(65)
        
        # 3. Apply text offset and expand space for the stacked \n text
        bottom_axis.setStyle(tickTextOffset=5, autoExpandTextSpace=True)

    def prepare_ai_stream(self):
        # --- THE FIX: Switch the Tab visuals AND the Stacked Page ---
        self.tabs.setCurrentItem('ai')
        self.stacked_widget.setCurrentIndex(1)
        # -------------------------------------------------------------
        
        self.btn_request_ai_analysis.setEnabled(False)
        self.btn_request_ai_analysis.setText("Generating Directive...")
        self.ai_text_display.clear()
        self.ai_text_display.append("<b style='color: #00A67E;'>[SYSTEM]</b> Ingesting JSON Payload to Enterprise AI...")

    def stream_ai_response(self, stream_generator):
        self.worker = AIStreamWorker(stream_generator)
        self.worker.chunk_received.connect(self._append_chunk)
        self.worker.finished.connect(self._on_stream_finished)
        self.worker.start()

    def _append_chunk(self, chunk):
        self.ai_text_display.insertPlainText(chunk)
        scrollbar = self.ai_text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_stream_finished(self):
        self.btn_request_ai_analysis.setEnabled(True)
        self.btn_request_ai_analysis.setText("Refresh Supply Chain Strategy")
        final_markdown = self.ai_text_display.toPlainText()
        self.ai_text_display.setMarkdown(final_markdown)