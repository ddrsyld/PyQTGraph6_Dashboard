"""
BatteryTelemetry Model for BMS (12.8V LiFePO4 Pack)
Matches and expands upon the WPF BatteryTelemetry.cs model.
"""

from dataclasses import dataclass, field
from datetime import datetime
import math


@dataclass
class BatteryTelemetry:
    voltage: float = 13.20         # Volt (V) - Nominal 12.8V LiFePO4 (10.0V - 14.6V)
    current: float = 2.50          # Ampere (A) - ACS712 (-30A s/d +30A)
    temperature: float = 28.5      # Celsius (°C) - NTC 10K
    soc: float = 70.0              # State of Charge (0 - 100%)
    capacity_ah: float = 0.450     # Ah keluar / Coulomb counting
    nominal_capacity_ah: float = 100.0  # Kapasitas Nominal Pack (100 Ah)
    relay_active: bool = True      # Status Relay (True = ON/Connected, False = Cutoff)
    is_fault: bool = False         # Status Alarm Proteksi (True = Fault)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def power(self) -> float:
        """Daya listrik dalam Watt (W = V * I)"""
        return round(self.voltage * self.current, 2)

    @property
    def is_discharging(self) -> bool:
        return self.current > 0.10

    @property
    def is_charging(self) -> bool:
        return self.current < -0.10

    @property
    def remaining_ah(self) -> float:
        """Sisa kapasitas baterai dalam Ah"""
        return max(0.0, round(self.nominal_capacity_ah - self.capacity_ah, 2))

    @property
    def capacity_percentage(self) -> float:
        """Persentase kapasitas tersisa (0 - 100%)"""
        if self.nominal_capacity_ah > 0:
            val = (self.remaining_ah / self.nominal_capacity_ah) * 100.0
            return max(0.0, min(100.0, round(val, 1)))
        return 0.0

    @property
    def operating_mode(self) -> str:
        if self.is_discharging:
            return "DISCHARGING (+)"
        if self.is_charging:
            return "CHARGING (-)"
        return "STANDBY (0.0 A)"

    @property
    def relay_status_text(self) -> str:
        return "RELAY: ON (TERHUBUNG)" if self.relay_active else "RELAY: CUT-OFF (TERPUTUS)"

    @property
    def fault_status_text(self) -> str:
        return "ALARM FAULT!" if self.is_fault else "SISTEM NORMAL"

    @property
    def capacity_status(self) -> str:
        if self.capacity_ah >= 80:
            return "TINGGI (> 80 Ah)"
        if self.capacity_ah >= 40:
            return "SEDANG (40-80 Ah)"
        return "NORMAL (< 40 Ah)"

    @property
    def thermal_status(self) -> str:
        if self.temperature < 15:
            return "DINGIN (< 15°C)"
        if self.temperature <= 45:
            return "NORMAL (15-45°C)"
        if self.temperature <= 60:
            return "HANGAT (45-60°C)"
        return "THERMAL FAULT! (> 60°C)"

    @staticmethod
    def calculate_lifepo4_soc(voltage: float) -> float:
        """
        Rumus Interpolasi SOC LiFePO4 12V berdasarkan kurva resting voltage:
        10.0V -> 0% s/d 13.6V -> 100%
        """
        v_table = [10.0, 12.0, 12.8, 12.9, 13.0, 13.1, 13.2, 13.3, 13.4, 13.6]
        soc_table = [0.0, 10.0, 20.0, 30.0, 45.0, 60.0, 70.0, 80.0, 90.0, 100.0]

        if voltage <= v_table[0]:
            return 0.0
        if voltage >= v_table[-1]:
            return 100.0

        for i in range(len(v_table) - 1):
            if voltage <= v_table[i + 1]:
                fraction = (voltage - v_table[i]) / (v_table[i + 1] - v_table[i])
                return round(soc_table[i] + fraction * (soc_table[i + 1] - soc_table[i]), 1)

        return 100.0
