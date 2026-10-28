"""
Universal Data Parser for BMS Telemetry
Supports JSON, Key-Value string, and CSV formats.
"""

import json
import re
from typing import Optional
from models.telemetry import BatteryTelemetry


class DataParser:
    @staticmethod
    def parse(raw: str) -> Optional[BatteryTelemetry]:
        if not raw or not raw.strip():
            return None
        
        line = raw.strip()

        # 1. Try parsing JSON
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)
                # Helper to get case-insensitive key
                def get_val(*keys, default=0.0):
                    for k in keys:
                        for actual_k, val in data.items():
                            if actual_k.lower() == k.lower():
                                try:
                                    return float(val)
                                except (ValueError, TypeError):
                                    pass
                    return default

                v = get_val("v", "voltage", "tegangan", default=0.0)
                i = get_val("i", "current", "arus", default=0.0)
                t = get_val("t", "temp", "temperature", "suhu", default=25.0)
                soc = get_val("soc", "charge", default=-1.0)
                ah = get_val("ah", "cap", "capacity", "ampere_hour", "discharged", "soh", default=0.0)

                # Relay status
                relay = True
                for rk in ["relay", "relay_active", "status_relay"]:
                    for actual_k, val in data.items():
                        if actual_k.lower() == rk:
                            if isinstance(val, (int, float)):
                                relay = bool(int(val) != 0)
                            elif isinstance(val, str):
                                relay = val.strip().lower() in ["1", "true", "on", "connected"]
                            elif isinstance(val, bool):
                                relay = val

                # Fault status
                fault = False
                for fk in ["fault", "alarm", "is_fault"]:
                    for actual_k, val in data.items():
                        if actual_k.lower() == fk:
                            if isinstance(val, (int, float)):
                                fault = bool(int(val) != 0)
                            elif isinstance(val, str):
                                fault = val.strip().lower() in ["1", "true", "fault", "alarm"]
                            elif isinstance(val, bool):
                                fault = val

                if soc < 0 and v > 0:
                    soc = BatteryTelemetry.calculate_lifepo4_soc(v)

                return BatteryTelemetry(
                    voltage=round(v, 2),
                    current=round(i, 2),
                    temperature=round(t, 1),
                    soc=max(0.0, min(100.0, round(soc, 1))),
                    capacity_ah=round(ah, 3),
                    relay_active=relay,
                    is_fault=fault
                )
            except Exception:
                pass

        # 2. Try parsing Key-Value / Text format from sketch.ino:
        # e.g.: "Tegangan: 13.20 V | Arus: 2.10 A | Suhu: 28.5 C | SOC: 70.0% | Ah keluar: 0.123 | Status: NORMAL"
        if ":" in line or "=" in line:
            try:
                def regex_extract(pattern: str) -> float:
                    m = re.search(pattern, line, re.IGNORECASE)
                    if m:
                        try:
                            return float(m.group(1))
                        except (ValueError, TypeError):
                            pass
                    return 0.0

                v = regex_extract(r'(?:V|VOLTAGE|TEGANGAN)\s*[:=]\s*([+-]?\d+(?:\.\d+)?)')
                i = regex_extract(r'(?:I|CURRENT|ARUS)\s*[:=]\s*([+-]?\d+(?:\.\d+)?)')
                t = regex_extract(r'(?:T|TEMP|TEMPERATURE|SUHU)\s*[:=]\s*([+-]?\d+(?:\.\d+)?)')
                soc = regex_extract(r'(?:SOC|CHARGE)\s*[:=]\s*([+-]?\d+(?:\.\d+)?)')
                ah = regex_extract(r'(?:AH|AH\s*KELUAR|CAP|CAPACITY|DISCHARGED|SOH)\s*[:=]\s*([+-]?\d+(?:\.\d+)?)')

                is_fault = "FAULT" in line.upper()
                relay = not is_fault

                if v > 0 or abs(i) > 0 or soc > 0:
                    if soc <= 0 and v > 0:
                        soc = BatteryTelemetry.calculate_lifepo4_soc(v)

                    return BatteryTelemetry(
                        voltage=round(v, 2),
                        current=round(i, 2),
                        temperature=round(t, 1) if t > 0 else 25.0,
                        soc=max(0.0, min(100.0, round(soc, 1))),
                        capacity_ah=round(ah, 3),
                        relay_active=relay,
                        is_fault=is_fault
                    )
            except Exception:
                pass

        # 3. Try parsing CSV: 13.20,2.10,28.5,70.0,0.123
        delim = ";" if ";" in line else ","
        parts = [p.strip() for p in line.split(delim)]
        if len(parts) >= 5:
            try:
                v = float(parts[0])
                i = float(parts[1])
                t = float(parts[2])
                soc = float(parts[3])
                ah = float(parts[4])
                return BatteryTelemetry(
                    voltage=round(v, 2),
                    current=round(i, 2),
                    temperature=round(t, 1),
                    soc=max(0.0, min(100.0, round(soc, 1))),
                    capacity_ah=round(ah, 3),
                    relay_active=True,
                    is_fault=False
                )
            except (ValueError, TypeError):
                pass

        return None
