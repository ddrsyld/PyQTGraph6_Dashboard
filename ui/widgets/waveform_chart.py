"""
Monochrome Real-Time Telemetry Waveform Chart
Uses PyQtGraph with strict high-contrast Black & White curves and grid lines.
"""

from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import pyqtgraph as pg


class WaveformChart(QWidget):
    def __init__(self, max_points: int = 60, parent=None):
        super().__init__(parent)
        self.max_points = max_points

        # Data history buffers
        self.voltage_history = deque(maxlen=max_points)
        self.current_history = deque(maxlen=max_points)
        self.temp_history = deque(maxlen=max_points)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # PyQtGraph PlotWidget setup
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("#000000")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setMouseEnabled(x=False, y=True)

        styles = {"color": "#888888", "font-size": "9px"}
        self.plot_widget.setLabel("left", "Nilai (V / A / °C)", **styles)
        self.plot_widget.setLabel("bottom", "Sampel Waktu (5 Hz)", **styles)

        # 1. Voltage Curve: Solid Pure White
        v_pen = pg.mkPen(color="#ffffff", width=2.2)
        self.v_curve = self.plot_widget.plot(name="Tegangan (V)", pen=v_pen)

        # 2. Current Curve: Dashed Light Gray
        i_pen = pg.mkPen(color="#aaaaaa", width=1.8, style=Qt.PenStyle.DashLine)
        self.i_curve = self.plot_widget.plot(name="Arus (A)", pen=i_pen)

        # 3. Temp Curve: Dotted Mid Gray
        t_pen = pg.mkPen(color="#555555", width=1.5, style=Qt.PenStyle.DotLine)
        self.t_curve = self.plot_widget.plot(name="Suhu (°C)", pen=t_pen)

        layout.addWidget(self.plot_widget)

    def set_theme(self, is_dark: bool):
        if is_dark:
            self.plot_widget.setBackground("#000000")
            self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
            self.v_curve.setPen(pg.mkPen(color="#ffffff", width=2.2))
            self.i_curve.setPen(pg.mkPen(color="#aaaaaa", width=1.8, style=Qt.PenStyle.DashLine))
            self.t_curve.setPen(pg.mkPen(color="#555555", width=1.5, style=Qt.PenStyle.DotLine))
        else:
            self.plot_widget.setBackground("#ffffff")
            self.plot_widget.showGrid(x=True, y=True, alpha=0.25)
            self.v_curve.setPen(pg.mkPen(color="#000000", width=2.2))
            self.i_curve.setPen(pg.mkPen(color="#555555", width=1.8, style=Qt.PenStyle.DashLine))
            self.t_curve.setPen(pg.mkPen(color="#888888", width=1.5, style=Qt.PenStyle.DotLine))

    def push_data(self, voltage: float, current: float, temperature: float):
        self.voltage_history.append(voltage)
        self.current_history.append(current)
        self.temp_history.append(temperature)

        x_data = list(range(len(self.voltage_history)))
        self.v_curve.setData(x_data, list(self.voltage_history))
        self.i_curve.setData(x_data, list(self.current_history))
        self.t_curve.setData(x_data, list(self.temp_history))

    def clear(self):
        self.voltage_history.clear()
        self.current_history.clear()
        self.temp_history.clear()
        self.v_curve.clear()
        self.i_curve.clear()
        self.t_curve.clear()
