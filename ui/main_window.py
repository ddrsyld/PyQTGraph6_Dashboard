"""
Main Window for BMS Telemetry Dashboard (Python Edition)
Strict Black & White Industrial Aesthetic. Zero AI-slop, no emojis/stickers.
Accurate multi-tier connection state tracking (Offline -> Waiting Data -> Streaming Online).
"""

import os
import random
import time
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QFrame, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont, QPixmap

from models.telemetry import BatteryTelemetry
from services.mqtt_service import MqttService
from services.serial_service import SerialService
from ui.themes import BLACK_WHITE_THEME, WHITE_BLACK_THEME
from ui.widgets.kpi_card import KpiCard
from ui.widgets.battery_widget import BatteryWidget
from ui.widgets.arc_gauge import ArcGauge
from ui.widgets.waveform_chart import WaveformChart


class BridgeSignals(QObject):
    """Thread-safe signal bridge between background MQTT/Serial threads and Qt UI."""
    raw_data_received = pyqtSignal(str)
    telemetry_parsed = pyqtSignal(object)
    connection_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)
    system_log = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CELLGUYS BMS // TELEMETRY & PROTECTION MONITOR - SIC 8")
        self.resize(1280, 780)
        self.setMinimumSize(1050, 620)

        # State Variables
        self.is_dark_mode = True
        self.logo_variant = "auto"
        self.is_simulation_running = False
        self.is_transport_connected = False  # TCP/Port connected to broker/serial
        self.packet_counter = 0
        self.last_packet_time: Optional[float] = None
        self.packets_in_last_sec = 0
        self.raw_logs_list = []
        self.min_voltage = 10.0
        self.max_voltage = 14.6
        self.max_current = 20.0
        self.max_temperature = 35.0

        # Services
        self.mqtt_service = MqttService()
        self.serial_service = SerialService()

        # Thread-safe Signals
        self.signals = BridgeSignals()
        self.signals.raw_data_received.connect(self._handle_raw_data)
        self.signals.telemetry_parsed.connect(self._handle_telemetry)
        self.signals.connection_changed.connect(self._handle_connection_state)
        self.signals.error_occurred.connect(self._handle_error)
        self.signals.system_log.connect(self._handle_system_log)

        # Wire Service Callbacks
        self.mqtt_service.on_raw_data_received = self.signals.raw_data_received.emit
        self.mqtt_service.on_telemetry_parsed = self.signals.telemetry_parsed.emit
        self.mqtt_service.on_connection_state_changed = self.signals.connection_changed.emit
        self.mqtt_service.on_error = self.signals.error_occurred.emit
        self.mqtt_service.on_system_log = self.signals.system_log.emit

        self.serial_service.on_raw_data_received = self.signals.raw_data_received.emit
        self.serial_service.on_telemetry_parsed = self.signals.telemetry_parsed.emit
        self.serial_service.on_connection_state_changed = self.signals.connection_changed.emit
        self.serial_service.on_error = self.signals.error_occurred.emit
        self.serial_service.on_system_log = self.signals.system_log.emit

        # Heartbeat & Health Check Timer (Every 1000ms)
        self.health_timer = QTimer(self)
        self.health_timer.setInterval(1000)
        self.health_timer.timeout.connect(self._health_check_tick)
        self.health_timer.start()

        # Simulation Demo Timer
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(500)
        self.sim_timer.timeout.connect(self._simulation_tick)

        # Current telemetry state
        self.current_telemetry = BatteryTelemetry()

        # Build UI
        self._setup_ui()
        self._apply_theme()
        self._refresh_serial_ports()

        # Pre-seed initial history
        self._initialize_dummy_history()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(12)

        # -------------------------------------------------------------
        # ROW 0: HEADER & CONNECTION BAR
        # -------------------------------------------------------------
        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(14, 10, 14, 10)
        header_layout.setSpacing(12)

        # CellGuys Official Logo
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_label.setToolTip("CellGuys Official Logo (Klik untuk switch varian warna / monokrom)")
        self.logo_label.mousePressEvent = self._cycle_logo_variant
        header_layout.addWidget(self.logo_label)

        # Title Box
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        app_title = QLabel("BMS TELEMETRY MONITOR")
        app_title.setStyleSheet("font-size: 15px; font-weight: 900; letter-spacing: 0.8px;")
        title_box.addWidget(app_title)

        app_sub = QLabel("12.8V 4S LiFePO4 Inovasi BMS // SIC Stage 2 Final Project")
        app_sub.setStyleSheet("font-size: 10px; color: #888888;")
        title_box.addWidget(app_sub)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Connection Mode Selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["MQTT (Wokwi / IoT)", "SERIAL (RS-232 / COM)"])
        self.mode_combo.setFixedWidth(150)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        header_layout.addWidget(self.mode_combo)

        # MQTT Controls
        self.mqtt_box = QWidget()
        mqtt_layout = QHBoxLayout(self.mqtt_box)
        mqtt_layout.setContentsMargins(0, 0, 0, 0)
        mqtt_layout.setSpacing(6)

        self.broker_combo = QComboBox()
        self.broker_combo.setEditable(True)
        # Put broker.emqx.io first as configured in bms_wokwi_simulation.ino!
        self.broker_combo.addItems(["broker.emqx.io", "broker.hivemq.com", "test.mosquitto.org", "localhost"])
        self.broker_combo.setFixedWidth(155)
        self.broker_combo.setToolTip("Alamat Broker MQTT (default Wokwi: broker.emqx.io)")
        mqtt_layout.addWidget(self.broker_combo)

        self.topic_input = QLineEdit("sic/bms/telemetry")
        self.topic_input.setFixedWidth(130)
        self.topic_input.setToolTip("Topic MQTT (default: sic/bms/telemetry)")
        mqtt_layout.addWidget(self.topic_input)
        header_layout.addWidget(self.mqtt_box)

        # Serial Controls
        self.serial_box = QWidget()
        serial_layout = QHBoxLayout(self.serial_box)
        serial_layout.setContentsMargins(0, 0, 0, 0)
        serial_layout.setSpacing(6)

        self.port_combo = QComboBox()
        self.port_combo.setFixedWidth(110)
        self.port_combo.setToolTip("Pilih Port Serial Virtual/Fisik")
        serial_layout.addWidget(self.port_combo)

        self.btn_refresh_ports = QPushButton("REFRESH")
        self.btn_refresh_ports.clicked.connect(self._refresh_serial_ports)
        serial_layout.addWidget(self.btn_refresh_ports)

        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("115200")
        self.baud_combo.setFixedWidth(80)
        serial_layout.addWidget(self.baud_combo)

        header_layout.addWidget(self.serial_box)
        self.serial_box.hide()

        # Connect / Disconnect Button (Solid White)
        self.btn_connect = QPushButton("HUBUNGKAN")
        self.btn_connect.setObjectName("primaryBtn")
        self.btn_connect.setFixedWidth(105)
        self.btn_connect.clicked.connect(self._toggle_connection)
        header_layout.addWidget(self.btn_connect)

        # Connection Health Badge Pill
        self.conn_pill = QFrame()
        self.conn_pill.setObjectName("cardAlt")
        pill_layout = QHBoxLayout(self.conn_pill)
        pill_layout.setContentsMargins(8, 4, 8, 4)
        pill_layout.setSpacing(6)

        self.conn_status_badge = QLabel("OFFLINE")
        self.conn_status_badge.setObjectName("badgeNormal")
        pill_layout.addWidget(self.conn_status_badge)
        header_layout.addWidget(self.conn_pill)

        # Simulation Demo Button
        self.btn_simulation = QPushButton("SIMULASI DEMO")
        self.btn_simulation.clicked.connect(self._toggle_simulation)
        header_layout.addWidget(self.btn_simulation)

        # Theme Switcher (Monochrome Toggle)
        self.btn_theme = QPushButton("THEME")
        self.btn_theme.setToolTip("Ganti Tampilan Hitam / Putih")
        self.btn_theme.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.btn_theme)

        main_layout.addWidget(header_card)

        # -------------------------------------------------------------
        # ROW 1: 5 PRIMARY KPI CARDS (STRICT B&W)
        # -------------------------------------------------------------
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(10)

        self.card_voltage = KpiCard("Tegangan", "V", "NOMINAL 12.8V")
        self.card_voltage.set_detail("MIN / MAX", "10.0V / 14.6V")
        kpi_grid.addWidget(self.card_voltage, 0, 0)

        self.card_current = KpiCard("Arus", "A", "STANDBY")
        self.card_current.set_detail("DAYA (P = V x I)", "0.0 W")
        kpi_grid.addWidget(self.card_current, 0, 1)

        self.card_temp = KpiCard("Suhu Sensor", "°C", "NORMAL")
        self.card_temp.set_detail("BATAS AMAN", "< 60.0 °C")
        kpi_grid.addWidget(self.card_temp, 0, 2)

        self.card_soc = KpiCard("SOC (Charge)", "%", "KAPASITAS", has_progress=True)
        self.card_soc.set_detail("KAPASITAS SISA", "70.0 Ah / 100 Ah")
        kpi_grid.addWidget(self.card_soc, 0, 3)

        self.card_capacity = KpiCard("Ah Keluar", "Ah", "COULOMB COUNT", has_progress=True)
        self.card_capacity.set_detail("STATUS SISTEM", "SISTEM NORMAL")
        kpi_grid.addWidget(self.card_capacity, 0, 4)

        main_layout.addLayout(kpi_grid)

        # -------------------------------------------------------------
        # ROW 2: MAIN VISUALIZATION (LEFT: CELL & ARCS, RIGHT: WAVEFORM)
        # -------------------------------------------------------------
        center_layout = QHBoxLayout()
        center_layout.setSpacing(12)

        # LEFT PANEL: BATTERY CELL GRAPHIC & SOH GAUGE (~450px)
        left_card = QFrame()
        left_card.setObjectName("card")
        left_card.setFixedWidth(450)
        left_vbox = QVBoxLayout(left_card)
        left_vbox.setContentsMargins(14, 12, 14, 12)
        left_vbox.setSpacing(10)

        # Left Panel Header
        left_head = QHBoxLayout()
        left_title = QLabel("VISUALISASI PACK 12.8V LiFePO4")
        left_title.setObjectName("sectionTitle")
        left_head.addWidget(left_title)
        left_head.addStretch()

        self.relay_badge = QLabel("RELAY: ON")
        self.relay_badge.setObjectName("badgeHighlight")
        left_head.addWidget(self.relay_badge)
        left_vbox.addLayout(left_head)

        # Left Content Row
        cell_row = QHBoxLayout()
        cell_row.setSpacing(12)

        # 1. Custom Monochrome Battery
        self.battery_visualizer = BatteryWidget()
        cell_row.addWidget(self.battery_visualizer)

        # 2. Right Side: Technical Specs + Arc Gauge
        spec_box = QVBoxLayout()
        spec_box.setSpacing(6)

        specs_card = QFrame()
        specs_card.setObjectName("cardAlt")
        specs_layout = QVBoxLayout(specs_card)
        specs_layout.setContentsMargins(10, 8, 10, 8)
        specs_layout.setSpacing(3)

        spec_header = QLabel("MODUL TELEMETRI")
        spec_header.setStyleSheet("font-size: 9px; font-weight: bold; color: #666666;")
        specs_layout.addWidget(spec_header)

        spec_model = QLabel("4S 12.8V LiFePO4 (100 Ah)")
        spec_model.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 2px;")
        specs_layout.addWidget(spec_model)

        def make_kv(k, v):
            h = QHBoxLayout()
            kl = QLabel(k)
            kl.setStyleSheet("font-size: 10px; color: #888888;")
            vl = QLabel(v)
            vl.setStyleSheet("font-size: 10px; font-weight: bold;")
            h.addWidget(kl)
            h.addStretch()
            h.addWidget(vl)
            return h, vl

        kv_imp, _ = make_kv("Impedansi:", "4.2 mΩ")
        specs_layout.addLayout(kv_imp)

        kv_prot, self.spec_prot_val = make_kv("Proteksi:", "SISTEM NORMAL")
        specs_layout.addLayout(kv_prot)

        kv_ah, self.spec_ah_val = make_kv("Ah Keluar:", "0.450 Ah")
        specs_layout.addLayout(kv_ah)

        spec_box.addWidget(specs_card)

        # Radial Arc Gauge Card
        arc_card = QFrame()
        arc_card.setObjectName("cardAlt")
        arc_layout = QHBoxLayout(arc_card)
        arc_layout.setContentsMargins(6, 6, 6, 6)
        arc_layout.setSpacing(8)

        self.arc_gauge = ArcGauge()
        arc_layout.addWidget(self.arc_gauge)

        arc_info = QVBoxLayout()
        arc_info.setSpacing(2)
        arc_info_title = QLabel("COULOMB COUNTING")
        arc_info_title.setStyleSheet("font-size: 8px; font-weight: bold; color: #666666;")
        arc_info.addWidget(arc_info_title)

        self.arc_status_label = QLabel("NORMAL (< 40 Ah)")
        self.arc_status_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #ffffff;")
        arc_info.addWidget(self.arc_status_label)

        self.arc_rem_label = QLabel("Sisa: 70.0 Ah / 100 Ah")
        self.arc_rem_label.setStyleSheet("font-size: 9px; color: #888888;")
        self.arc_rem_label.setWordWrap(True)
        arc_info.addWidget(self.arc_rem_label)
        arc_layout.addLayout(arc_info)

        spec_box.addWidget(arc_card)
        cell_row.addLayout(spec_box)
        left_vbox.addLayout(cell_row)

        # Control Action Buttons
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(8)

        self.btn_reset_alarm = QPushButton("RESET ALARM")
        self.btn_reset_alarm.setToolTip("Kirim perintah reset alarm ke ESP32")
        self.btn_reset_alarm.clicked.connect(self._send_reset_alarm)
        ctrl_bar.addWidget(self.btn_reset_alarm)

        self.btn_toggle_relay = QPushButton("TOGGLE RELAY")
        self.btn_toggle_relay.setToolTip("Kirim perintah ON/OFF relay ke ESP32")
        self.btn_toggle_relay.clicked.connect(self._send_toggle_relay)
        ctrl_bar.addWidget(self.btn_toggle_relay)

        left_vbox.addLayout(ctrl_bar)

        # Diagnostics / Status Bar at bottom of Left Panel
        proto_bar = QFrame()
        proto_bar.setObjectName("cardAlt")
        proto_layout = QVBoxLayout(proto_bar)
        proto_layout.setContentsMargins(8, 6, 8, 6)
        proto_layout.setSpacing(2)

        self.status_bar_label = QLabel("OFFLINE: Pilih broker/port lalu klik HUBUNGKAN")
        self.status_bar_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #ffffff;")
        proto_layout.addWidget(self.status_bar_label)

        self.diag_hint_label = QLabel("Hint: Jalankan simulasi Wokwi di browser untuk mulai menerima data.")
        self.diag_hint_label.setStyleSheet("font-size: 9px; color: #777777;")
        proto_layout.addWidget(self.diag_hint_label)

        left_vbox.addWidget(proto_bar)
        center_layout.addWidget(left_card)

        # RIGHT PANEL: REAL-TIME TELEMETRY WAVEFORM GRAPH
        right_card = QFrame()
        right_card.setObjectName("card")
        right_vbox = QVBoxLayout(right_card)
        right_vbox.setContentsMargins(16, 12, 16, 12)
        right_vbox.setSpacing(8)

        # Waveform Header
        wave_head = QHBoxLayout()
        wave_title_box = QVBoxLayout()
        wave_title_box.setSpacing(2)
        wave_title = QLabel("WAVEFORM TELEMETRI REAL-TIME")
        wave_title.setObjectName("sectionTitle")
        wave_title_box.addWidget(wave_title)

        wave_sub = QLabel("Tren dinamika sensor 60 sampel terakhir (Frekuensi sampling 5 Hz)")
        wave_sub.setStyleSheet("font-size: 9px; color: #666666;")
        wave_title_box.addWidget(wave_sub)
        wave_head.addLayout(wave_title_box)
        wave_head.addStretch()

        # Monochrome Legend Labels
        def make_legend_item(text, symbol_text):
            hl = QHBoxLayout()
            hl.setSpacing(4)
            line = QLabel(symbol_text)
            line.setStyleSheet("color: #ffffff; font-weight: bold;")
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 9px; font-weight: 600; color: #888888;")
            hl.addWidget(line)
            hl.addWidget(lbl)
            return hl

        wave_head.addLayout(make_legend_item("Tegangan (V)", "━━━"))
        wave_head.addSpacing(10)
        wave_head.addLayout(make_legend_item("Arus (A)", "┅┅┅"))
        wave_head.addSpacing(10)
        wave_head.addLayout(make_legend_item("Suhu (°C)", "···"))

        right_vbox.addLayout(wave_head)

        # Waveform Chart Widget
        self.waveform_chart = WaveformChart(max_points=60)
        right_vbox.addWidget(self.waveform_chart, stretch=1)

        # Real-time Values & Packet Counter below chart
        wave_footer = QHBoxLayout()
        self.readout_label = QLabel("NILAI TERAKHIR:  V=13.20V  |  I=2.50A  |  T=28.5°C")
        self.readout_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #ffffff; font-family: monospace;")
        wave_footer.addWidget(self.readout_label)
        wave_footer.addStretch()

        self.packet_label = QLabel("PAKET: 0  |  RATE: 0.0 Hz")
        self.packet_label.setStyleSheet("font-size: 10px; font-weight: 800; color: #aaaaaa; font-family: monospace;")
        wave_footer.addWidget(self.packet_label)
        right_vbox.addLayout(wave_footer)

        center_layout.addWidget(right_card, stretch=1)
        main_layout.addLayout(center_layout, stretch=1)

        # -------------------------------------------------------------
        # ROW 3: RAW PACKET MONITOR & DIAGNOSTICS CONSOLE
        # -------------------------------------------------------------
        console_card = QFrame()
        console_card.setObjectName("card")
        console_vbox = QVBoxLayout(console_card)
        console_vbox.setContentsMargins(12, 8, 12, 8)
        console_vbox.setSpacing(6)

        console_head = QHBoxLayout()
        console_title = QLabel("RAW TELEMETRY STREAM & LOG")
        console_title.setObjectName("sectionTitle")
        console_head.addWidget(console_title)

        autodetect_pill = QLabel("AUTO-PARSER: JSON / CSV / KV")
        autodetect_pill.setObjectName("badgeNormal")
        console_head.addWidget(autodetect_pill)
        console_head.addStretch()

        self.btn_export_csv = QPushButton("EXPORT CSV")
        self.btn_export_csv.clicked.connect(self._export_csv)
        console_head.addWidget(self.btn_export_csv)

        self.btn_clear_log = QPushButton("BERSIHKAN LOG")
        self.btn_clear_log.clicked.connect(self._clear_logs)
        console_head.addWidget(self.btn_clear_log)

        self.btn_toggle_log = QPushButton("SEMBUNYIKAN LOG")
        self.btn_toggle_log.clicked.connect(self._toggle_log_console)
        console_head.addWidget(self.btn_toggle_log)

        console_vbox.addLayout(console_head)

        self.terminal_console = QTextEdit()
        self.terminal_console.setObjectName("terminalConsole")
        self.terminal_console.setFixedHeight(95)
        self.terminal_console.setReadOnly(True)
        self.terminal_console.append("[System] CELLGUYS BMS Telemetry Core v2.4 initialized. Ready for connection.")
        console_vbox.addWidget(self.terminal_console)

        main_layout.addWidget(console_card)

    # -------------------------------------------------------------
    # CONNECTION & HEALTH MONITORING
    # -------------------------------------------------------------
    def _health_check_tick(self):
        """Called every 1 second to verify packet flow and update status."""
        rate = self.packets_in_last_sec
        self.packets_in_last_sec = 0

        if not self.is_transport_connected:
            self.conn_status_badge.setText("OFFLINE")
            self.conn_status_badge.setObjectName("badgeNormal")
            self.status_bar_label.setText("OFFLINE: Belum terhubung")
            self.diag_hint_label.setText("Pilih broker/port lalu klik tombol HUBUNGKAN.")
            self.packet_label.setText(f"PAKET: {self.packet_counter:,}  |  RATE: 0.0 Hz")
            self.conn_status_badge.setStyle(self.conn_status_badge.style())
            return

        now = time.time()
        is_mqtt = self.mode_combo.currentIndex() == 0
        target_name = self.broker_combo.currentText().strip() if is_mqtt else self.port_combo.currentText()

        # Check if we have received ANY packet
        if self.last_packet_time is None:
            # Connected to broker, but 0 packets ever arrived
            self.conn_status_badge.setText("WAITING DATA")
            self.conn_status_badge.setObjectName("badgeWarning")
            self.status_bar_label.setText(f"BROKER OK: Menunggu data dari ESP32 ({target_name})")
            if is_mqtt:
                self.diag_hint_label.setText("Pastikan Wokwi sedang RUNNING di browser dan broker di sketch adalah " + target_name)
            else:
                self.diag_hint_label.setText(f"Port {target_name} terbuka. Menunggu data serial dari mikrokontroler.")
            self.packet_label.setText(f"PAKET: 0  |  RATE: 0.0 Hz")
        else:
            idle_seconds = now - self.last_packet_time
            if idle_seconds <= 3.0:
                # Active streaming
                self.conn_status_badge.setText("ONLINE STREAMING")
                self.conn_status_badge.setObjectName("badgeHighlight")
                self.status_bar_label.setText(f"STREAMING AKTIF: Menerima data dari {target_name}")
                self.diag_hint_label.setText(f"Telemetri normal. Terakhir diterima: {idle_seconds:.1f}s lalu.")
                self.packet_label.setText(f"PAKET: {self.packet_counter:,}  |  RATE: {rate:.1f} Hz")
            else:
                # Idle / Paused
                self.conn_status_badge.setText(f"IDLE ({int(idle_seconds)}s)")
                self.conn_status_badge.setObjectName("badgeWarning")
                self.status_bar_label.setText(f"TIDAK ADA DATA: Terhenti sejak {int(idle_seconds)} detik lalu")
                self.diag_hint_label.setText("Periksa apakah simulasi Wokwi di-pause atau koneksi WiFi ESP32 terputus.")
                self.packet_label.setText(f"PAKET: {self.packet_counter:,}  |  RATE: 0.0 Hz")

        self.conn_status_badge.setStyle(self.conn_status_badge.style())

    def _on_mode_changed(self, index: int):
        is_mqtt = index == 0
        if is_mqtt:
            self.mqtt_box.show()
            self.serial_box.hide()
            self.status_bar_label.setText(f"Mode MQTT aktif (Broker: {self.broker_combo.currentText()})")
        else:
            self.mqtt_box.hide()
            self.serial_box.show()
            self.status_bar_label.setText("Mode Serial Port aktif")

    def _refresh_serial_ports(self):
        self.port_combo.clear()
        ports = SerialService.get_available_ports()
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItems(["COM1 (Virtual)", "COM2 (Virtual)"])

    def _toggle_connection(self):
        if self.is_transport_connected:
            self.mqtt_service.disconnect()
            self.serial_service.disconnect()
            self.is_transport_connected = False
            self.last_packet_time = None
            self.btn_connect.setText("HUBUNGKAN")
            self._handle_system_log("[System] Koneksi diputus oleh pengguna.")
            self._health_check_tick()
        else:
            is_mqtt = self.mode_combo.currentIndex() == 0
            if is_mqtt:
                broker = self.broker_combo.currentText().strip()
                topic = self.topic_input.text().strip()
                if not broker:
                    QMessageBox.warning(self, "Peringatan", "Masukkan alamat MQTT broker!")
                    return
                self._handle_system_log(f"[System] Menghubungkan ke MQTT Broker: {broker}:1883...")
                self._handle_system_log(f"[System] Target Topic: {topic} dan sic/bms/#")
                self.status_bar_label.setText(f"Menghubungkan ke {broker}...")
                self.last_packet_time = None
                self.mqtt_service.connect(broker=broker, port=1883, topic=topic)
            else:
                port = self.port_combo.currentText()
                baud = int(self.baud_combo.currentText())
                if not port:
                    QMessageBox.warning(self, "Peringatan", "Pilih Port Serial terlebih dahulu!")
                    return
                self._handle_system_log(f"[System] Membuka port serial {port} @ {baud} bps...")
                self.status_bar_label.setText(f"Menghubungkan ke {port}...")
                self.last_packet_time = None
                self.serial_service.connect(port_name=port, baud_rate=baud)

    def _handle_connection_state(self, connected: bool, message: str):
        self.is_transport_connected = connected
        if connected:
            self.btn_connect.setText("PUTUSKAN")
        else:
            self.btn_connect.setText("HUBUNGKAN")
            self.last_packet_time = None
        self._health_check_tick()

    def _handle_system_log(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.terminal_console.append(f"[{ts}] {text}")

    def _handle_raw_data(self, raw_str: str):
        self.packet_counter += 1
        self.packets_in_last_sec += 1
        self.last_packet_time = time.time()

        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"[{ts}] >> {raw_str}"
        self.raw_logs_list.append((ts, raw_str))
        if len(self.raw_logs_list) > 300:
            self.raw_logs_list.pop(0)

        self.terminal_console.append(log_line)
        # Limit buffer
        if len(self.terminal_console.toPlainText()) > 20000:
            self.terminal_console.clear()

        self._health_check_tick()

    def _handle_telemetry(self, t: BatteryTelemetry):
        self.current_telemetry = t

        # Update Extrema
        if t.voltage < self.min_voltage or self.min_voltage == 0:
            self.min_voltage = t.voltage
        if t.voltage > self.max_voltage:
            self.max_voltage = t.voltage
        if abs(t.current) > self.max_current:
            self.max_current = abs(t.current)
        if t.temperature > self.max_temperature:
            self.max_temperature = t.temperature

        # 1. Update KPI Cards (Monochrome)
        self.card_voltage.set_value(f"{t.voltage:.2f}")
        self.card_voltage.set_detail("MIN / MAX", f"{self.min_voltage:.1f}V / {self.max_voltage:.1f}V")

        self.card_current.set_value(f"{t.current:.2f}")
        self.card_current.set_badge(t.operating_mode, "highlight" if t.is_charging else "normal")
        self.card_current.set_detail("DAYA (P = V x I)", f"{t.power:.1f} W")

        self.card_temp.set_value(f"{t.temperature:.1f}")
        t_mode = "warning" if t.temperature > 50 else "normal"
        self.card_temp.set_badge(t.thermal_status, t_mode)
        self.card_temp.set_detail("BATAS AMAN", f"< 60.0 °C (MAX: {self.max_temperature:.1f}°C)")

        self.card_soc.set_value(f"{t.soc:.1f}")
        self.card_soc.set_progress(t.soc)
        self.card_soc.set_detail("KAPASITAS SISA", f"{t.remaining_ah:.1f} Ah / 100 Ah")

        self.card_capacity.set_value(f"{t.capacity_ah:.3f}")
        self.card_capacity.set_progress(t.capacity_percentage)
        self.card_capacity.set_detail("STATUS SISTEM", t.fault_status_text)
        self.card_capacity.set_badge(t.fault_status_text, "warning" if t.is_fault else "normal")

        # 2. Update Battery Visualizer
        self.battery_visualizer.set_data(t.soc, t.is_charging, t.operating_mode)

        # 3. Update Left Panel Specs & Arc Gauge
        self.relay_badge.setText(t.relay_status_text)
        self.relay_badge.setObjectName("badgeHighlight" if t.relay_active else "badgeWarning")
        self.relay_badge.setStyle(self.relay_badge.style())

        self.spec_prot_val.setText(t.fault_status_text)
        self.spec_ah_val.setText(f"{t.capacity_ah:.3f} Ah")

        self.arc_gauge.set_data(t.capacity_percentage, f"{t.capacity_ah:.2f}")
        self.arc_status_label.setText(t.capacity_status)
        self.arc_rem_label.setText(f"Sisa: {t.remaining_ah:.1f} Ah / 100 Ah")

        # 4. Push to Waveform Chart
        self.waveform_chart.push_data(t.voltage, t.current, t.temperature)
        self.readout_label.setText(f"NILAI TERAKHIR:  V={t.voltage:.2f}V  |  I={t.current:.2f}A  |  T={t.temperature:.1f}°C")

    def _handle_error(self, err_msg: str):
        self._handle_system_log(f"[ERROR] {err_msg}")
        self.status_bar_label.setText(f"ERROR: {err_msg}")

    def _toggle_simulation(self):
        if self.is_simulation_running:
            self.sim_timer.stop()
            self.is_simulation_running = False
            self.btn_simulation.setText("SIMULASI DEMO")
            self._handle_system_log("[System] Simulasi Demo dihentikan.")
            if not self.is_transport_connected:
                self.is_transport_connected = False
                self.last_packet_time = None
            self._health_check_tick()
        else:
            self.sim_timer.start()
            self.is_simulation_running = True
            self.is_transport_connected = True
            self.btn_simulation.setText("STOP DEMO")
            self._handle_system_log("[System] Simulasi Demo aktif (Generator fluktuasi LiFePO4).")
            self._health_check_tick()

    def _simulation_tick(self):
        t = self.current_telemetry

        delta_v = (random.random() - 0.49) * 0.08
        t.voltage = round(max(10.5, min(14.2, t.voltage + delta_v)), 2)

        delta_i = (random.random() - 0.5) * 0.8
        t.current = round(max(-10.0, min(15.0, t.current + delta_i)), 2)

        delta_t = (random.random() - 0.49) * 0.1
        t.temperature = round(max(22.0, min(50.0, t.temperature + delta_t)), 1)

        t.soc = BatteryTelemetry.calculate_lifepo4_soc(t.voltage)

        if t.current > 0:
            t.capacity_ah = round(t.capacity_ah + (t.current * 0.0005), 3)

        raw_json = (
            f'{{"v":{t.voltage:.2f},"i":{t.current:.2f},"t":{t.temperature:.1f},'
            f'"soc":{t.soc:.1f},"ah":{t.capacity_ah:.3f},"relay":{1 if t.relay_active else 0},'
            f'"fault":{1 if t.is_fault else 0}}}'
        )

        self._handle_raw_data(raw_json)
        self._handle_telemetry(t)

    def _send_reset_alarm(self):
        cmd = '{"cmd":"reset_alarm"}'
        is_mqtt = self.mode_combo.currentIndex() == 0
        if is_mqtt:
            ctrl_topic = self.topic_input.text().strip() + "/control"
            sent = self.mqtt_service.publish(ctrl_topic, cmd)
            self._handle_system_log(f"[Command] Reset Alarm dipublish ke {ctrl_topic}" if sent else "[Command] Gagal: MQTT tidak terhubung")
        else:
            sent = self.serial_service.send_data(cmd)
            self._handle_system_log("[Command] Reset Alarm dikirim via Serial" if sent else "[Command] Gagal: Serial tidak terhubung")

        self.current_telemetry.is_fault = False
        self.current_telemetry.relay_active = True
        self._handle_telemetry(self.current_telemetry)

    def _send_toggle_relay(self):
        new_state = not self.current_telemetry.relay_active
        cmd = f'{{"cmd":"set_relay","state":{1 if new_state else 0}}}'
        is_mqtt = self.mode_combo.currentIndex() == 0
        if is_mqtt:
            ctrl_topic = self.topic_input.text().strip() + "/control"
            sent = self.mqtt_service.publish(ctrl_topic, cmd)
            self._handle_system_log(f"[Command] Toggle Relay ({new_state}) dipublish ke {ctrl_topic}" if sent else "[Command] Gagal: MQTT tidak terhubung")
        else:
            sent = self.serial_service.send_data(cmd)
            self._handle_system_log(f"[Command] Toggle Relay ({new_state}) dikirim via Serial" if sent else "[Command] Gagal: Serial tidak terhubung")

        self.current_telemetry.relay_active = new_state
        self._handle_telemetry(self.current_telemetry)

    def _export_csv(self):
        if not self.raw_logs_list:
            QMessageBox.information(self, "Export CSV", "Belum ada log data untuk diekspor.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Log Telemetri CSV",
            f"CellGuys_BMS_Telemetry_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Timestamp,Raw_Payload\n")
                    for ts, raw in self.raw_logs_list:
                        clean_raw = raw.replace('"', '""')
                        f.write(f'"{ts}","{clean_raw}"\n')
                QMessageBox.information(self, "Sukses", f"Log berhasil diekspor ke:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan file CSV:\n{e}")

    def _clear_logs(self):
        self.terminal_console.clear()
        self.raw_logs_list.clear()

    def _toggle_log_console(self):
        if self.terminal_console.isVisible():
            self.terminal_console.hide()
            self.btn_toggle_log.setText("TAMPILKAN LOG")
        else:
            self.terminal_console.show()
            self.btn_toggle_log.setText("SEMBUNYIKAN LOG")

    def _toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()

    def _get_logo_path(self, variant: str) -> str:
        import sys
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        filenames = {
            "white": "CELLGUYS_logo_white.png",
            "black": "CELLGUYS_logo_black.png",
            "accent": "CELLGUYS_logo_accent.png",
            "original": "CELLGUYS_logo_transparent.png",
        }
        target_fn = filenames.get(variant, "CELLGUYS_logo_white.png")
        candidates = [
            os.path.join(base_dir, "resources", target_fn),
            os.path.join(base_dir, target_fn),
            os.path.join(os.path.dirname(base_dir), target_fn),
            os.path.join("D:/dotnet/WPF/DashboardSIC1/Python_Version/resources", target_fn),
            os.path.join("D:/dotnet/WPF/DashboardSIC1", target_fn),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return candidates[0]

    def _update_logo(self):
        variant = self.logo_variant
        if variant == "auto":
            variant = "white" if self.is_dark_mode else "black"
        path = self._get_logo_path(variant)
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaledToHeight(38, Qt.TransformationMode.SmoothTransformation)
                self.logo_label.setPixmap(scaled)
                self.logo_label.setFixedSize(scaled.width(), scaled.height())

    def _cycle_logo_variant(self, event=None):
        variants = ["auto", "accent", "white", "black", "original"]
        current_idx = variants.index(self.logo_variant) if self.logo_variant in variants else 0
        self.logo_variant = variants[(current_idx + 1) % len(variants)]
        self._update_logo()
        self._handle_system_log(f"[System] Logo display mode: {self.logo_variant.upper()}")

    def _apply_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet(BLACK_WHITE_THEME)
            self.btn_theme.setText("MODE: DARK")
            self.waveform_chart.set_theme(is_dark=True)
        else:
            self.setStyleSheet(WHITE_BLACK_THEME)
            self.btn_theme.setText("MODE: LIGHT")
            self.waveform_chart.set_theme(is_dark=False)
        self._update_logo()

    def _initialize_dummy_history(self):
        base_v = 13.20
        base_i = 2.50
        base_t = 28.5

        for k in range(60):
            import math
            offset = math.sin(k * 0.15) * 0.25
            v = base_v + offset
            i = base_i + offset * 1.5
            t = base_t + (k * 0.05)
            self.waveform_chart.push_data(v, i, t)

        self._handle_telemetry(self.current_telemetry)

    def closeEvent(self, event):
        self.sim_timer.stop()
        self.health_timer.stop()
        self.mqtt_service.disconnect()
        self.serial_service.disconnect()
        event.accept()
