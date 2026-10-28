"""
CellGuys BMS - Telemetry Dashboard (Python Edition - Strict Monochrome)
Samsung Innovation Campus (SIC) Stage 2 - IoT Device & Hardware Discovery
Inovasi BMS LiFePO4 12.8V 4S
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    parser = argparse.ArgumentParser(description="CellGuys BMS Telemetry & Protection Dashboard - Python Edition")
    parser.add_argument("--simulate", action="store_true", help="Start immediately with demo simulation running")
    parser.add_argument("--broker", type=str, default="broker.emqx.io", help="Default MQTT Broker host (default: broker.emqx.io)")
    parser.add_argument("--topic", type=str, default="sic/bms/telemetry", help="Default MQTT Topic")
    parser.add_argument("--serial", action="store_true", help="Start with Serial mode active")
    args = parser.parse_args()

    # Enable High DPI scaling
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("CellGuys BMS Telemetry Dashboard - SIC 8")

    window = MainWindow()

    if args.broker:
        window.broker_combo.setCurrentText(args.broker)
    if args.topic:
        window.topic_input.setText(args.topic)
    if args.serial:
        window.mode_combo.setCurrentIndex(1)
    if args.simulate:
        window._toggle_simulation()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
