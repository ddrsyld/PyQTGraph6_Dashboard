"""
Monochrome Battery Visualizer Widget for LiFePO4 Pack
Strict Black & White styling, sharp vector outline, fluid level, and charging indicator.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from PyQt6.QtCore import Qt, QRectF


class BatteryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.soc = 70.0
        self.is_charging = False
        self.operating_mode = "STANDBY"
        self.setMinimumSize(120, 210)

    def set_data(self, soc: float, is_charging: bool, mode: str):
        self.soc = max(0.0, min(100.0, soc))
        self.is_charging = is_charging
        self.operating_mode = mode
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        cell_width = 96.0
        cell_height = 150.0
        top_cap_width = 34.0
        top_cap_height = 6.0

        x_cell = (w - cell_width) / 2.0
        y_top = 8.0
        y_cell = y_top + top_cap_height
        x_cap = (w - top_cap_width) / 2.0

        # 1. Terminal Cap (Solid White)
        cap_rect = QRectF(x_cap, y_top, top_cap_width, top_cap_height + 1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ffffff"))
        painter.drawRoundedRect(cap_rect, 2, 2)

        # 2. Battery Outer Casing (Black body with crisp White border)
        casing_rect = QRectF(x_cell, y_cell, cell_width, cell_height)
        painter.setPen(QPen(QColor("#ffffff"), 2.0))
        painter.setBrush(QColor("#0a0a0a"))
        painter.drawRoundedRect(casing_rect, 8, 8)

        # 3. Inner Fill (Monochrome Solid White Level)
        padding = 4.0
        inner_w = cell_width - (padding * 2)
        inner_h = cell_height - (padding * 2)
        fill_h = (self.soc / 100.0) * inner_h
        y_fill = (y_cell + cell_height - padding) - fill_h

        if fill_h > 1.0:
            fill_rect = QRectF(x_cell + padding, y_fill, inner_w, fill_h)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#ffffff"))
            painter.drawRoundedRect(fill_rect, 4, 4)

        # 4. Charging Bolt Indicator (Sharp Vector Icon)
        if self.is_charging:
            painter.save()
            bolt_path = QPainterPath()
            cx = w / 2.0
            cy = y_cell + 24.0

            bolt_path.moveTo(cx + 3, cy - 12)
            bolt_path.lineTo(cx - 6, cy + 1)
            bolt_path.lineTo(cx - 1, cy + 1)
            bolt_path.lineTo(cx - 3, cy + 12)
            bolt_path.lineTo(cx + 6, cy - 1)
            bolt_path.lineTo(cx + 1, cy - 1)
            bolt_path.closeSubpath()

            # Contrast outline
            painter.setPen(QPen(QColor("#000000"), 1.5))
            painter.setBrush(QColor("#ffffff"))
            painter.drawPath(bolt_path)
            painter.restore()

        # 5. Percentage Badge (Inverted Black Box on White Fill)
        badge_w = 60.0
        badge_h = 24.0
        badge_x = (w - badge_w) / 2.0
        badge_y = y_cell + (cell_height / 2.0) - (badge_h / 2.0)

        badge_rect = QRectF(badge_x, badge_y, badge_w, badge_h)
        painter.setPen(QPen(QColor("#ffffff"), 1.0))
        painter.setBrush(QColor("#000000"))
        painter.drawRoundedRect(badge_rect, 4, 4)

        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, f"{int(round(self.soc))}%")

        # 6. Operating Mode Text Below Casing
        mode_rect = QRectF(0, y_cell + cell_height + 6, w, 18)
        mode_font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(mode_font)
        painter.setPen(QColor("#888888"))
        painter.drawText(mode_rect, Qt.AlignmentFlag.AlignCenter, self.operating_mode)
