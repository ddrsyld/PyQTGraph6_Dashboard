"""
Monochrome KPI Metric Card Widget for BMS Telemetry
Clean Black and White design, high contrast, zero stickers/emojis.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class KpiCard(QFrame):
    def __init__(self, title: str, unit: str, subtitle: str = "", has_progress: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.unit = unit
        self.has_progress = has_progress

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header Row: Title & Subtitle Badge
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("sectionTitle")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.badge_label = QLabel(subtitle)
        self.badge_label.setObjectName("badgeNormal")
        self.badge_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.badge_label)
        layout.addLayout(header_layout)

        # Value Row: Big Value + Unit
        value_layout = QHBoxLayout()
        value_layout.setSpacing(4)
        self.value_label = QLabel("0.00")
        self.value_label.setStyleSheet("font-size: 26px; font-weight: 800; font-family: 'Segoe UI', monospace;")
        value_layout.addWidget(self.value_label)

        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #888888; margin-bottom: 3px;")
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        value_layout.addWidget(self.unit_label)
        value_layout.addStretch()
        layout.addLayout(value_layout)

        # Optional Progress Bar
        if has_progress:
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)
            self.progress_bar.setTextVisible(False)
            layout.addWidget(self.progress_bar)

        # Bottom Detail Row
        self.detail_layout = QHBoxLayout()
        self.detail_left = QLabel("INFO")
        self.detail_left.setStyleSheet("font-size: 9px; color: #666666; font-weight: 600; letter-spacing: 0.5px;")
        self.detail_right = QLabel("-")
        self.detail_right.setStyleSheet("font-size: 9px; color: #aaaaaa; font-weight: 600;")
        self.detail_layout.addWidget(self.detail_left)
        self.detail_layout.addStretch()
        self.detail_layout.addWidget(self.detail_right)
        layout.addLayout(self.detail_layout)

    def set_value(self, val_str: str):
        self.value_label.setText(val_str)

    def set_badge(self, text: str, mode: str = "normal"):
        self.badge_label.setText(text)
        if mode == "highlight":
            self.badge_label.setObjectName("badgeHighlight")
        elif mode == "warning":
            self.badge_label.setObjectName("badgeWarning")
        else:
            self.badge_label.setObjectName("badgeNormal")
        self.badge_label.setStyle(self.badge_label.style())

    def set_detail(self, left_text: str, right_text: str):
        self.detail_left.setText(left_text)
        self.detail_right.setText(right_text)

    def set_progress(self, percent: float):
        if self.has_progress:
            self.progress_bar.setValue(int(max(0, min(100, percent))))
