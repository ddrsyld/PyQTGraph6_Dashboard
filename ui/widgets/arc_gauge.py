"""
Monochrome Radial Arc Gauge Widget for BMS Telemetry
Clean Black and White design for Coulomb Counting / Capacity measurement.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF


class ArcGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percentage = 0.0
        self.value_text = "0.00"
        self.unit_text = "Ah keluar"
        self.setMinimumSize(85, 75)

    def set_data(self, percentage: float, value_text: str, unit_text: str = "Ah keluar"):
        self.percentage = max(0.0, min(100.0, percentage))
        self.value_text = value_text
        self.unit_text = unit_text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        size = min(w, h) - 12
        x = (w - size) / 2.0
        y = (h - size) / 2.0
        arc_rect = QRectF(x, y, size, size)

        start_angle = -210 * 16
        total_span = 240 * 16
        stroke_width = 6.0

        # 1. Background Track Arc (Dark Gray)
        track_pen = QPen(QColor("#242424"), stroke_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(arc_rect, start_angle, -total_span)

        # 2. Foreground Active Progress Arc (Pure White)
        active_span = int(-total_span * (self.percentage / 100.0))
        if active_span != 0:
            active_pen = QPen(QColor("#ffffff"), stroke_width)
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            painter.drawArc(arc_rect, start_angle, active_span)

        # 3. Center Value Text (Crisp White)
        painter.setPen(QColor("#ffffff"))
        val_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(val_font)
        val_rect = QRectF(0, y + 10, w, 20)
        painter.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, self.value_text)

        # 4. Center Unit Text (Muted Gray)
        painter.setPen(QColor("#888888"))
        unit_font = QFont("Segoe UI", 8, QFont.Weight.DemiBold)
        painter.setFont(unit_font)
        unit_rect = QRectF(0, y + 30, w, 16)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, self.unit_text)
