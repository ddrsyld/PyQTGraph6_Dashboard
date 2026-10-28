"""
Serial Port Service for BMS Dashboard using PySerial
Handles RS-232 / Virtual COM port communication, reading thread, and port enumeration.
"""

import threading
import time
from typing import Callable, List, Optional
import serial
import serial.tools.list_ports

from models.telemetry import BatteryTelemetry
from services.data_parser import DataParser


class SerialService:
    def __init__(self):
        self._serial: Optional[serial.Serial] = None
        self._read_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.current_port = ""
        self.current_baud = 115200

        # Callbacks
        self.on_raw_data_received: Optional[Callable[[str], None]] = None
        self.on_telemetry_parsed: Optional[Callable[[BatteryTelemetry], None]] = None
        self.on_connection_state_changed: Optional[Callable[[bool, str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_system_log: Optional[Callable[[str], None]] = None

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    @staticmethod
    def get_available_ports() -> List[str]:
        """Returns list of detected COM port device names."""
        try:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            return sorted(ports)
        except Exception:
            return []

    def connect(self, port_name: str, baud_rate: int = 115200) -> bool:
        """Connect to serial port and start background reader thread."""
        self.disconnect()

        clean_port = port_name.split()[0] if port_name else ""
        self.current_port = clean_port
        self.current_baud = baud_rate

        try:
            self._serial = serial.Serial(
                port=clean_port,
                baudrate=baud_rate,
                timeout=1.0,
                write_timeout=1.0
            )
            self._stop_event.clear()
            self._read_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self._read_thread.start()

            self._log(f"[OK] Port {clean_port} terbuka @ {baud_rate} bps")
            self._log("[INFO] Menunggu aliran data Serial...")
            if self.on_connection_state_changed:
                self.on_connection_state_changed(True, f"PORT TERBUKA | MENUNGGU DATA ({clean_port})")
            return True

        except Exception as ex:
            msg = f"Gagal buka port {clean_port}: {ex}"
            self._log(f"[ERROR] {msg}")
            if self.on_connection_state_changed:
                self.on_connection_state_changed(False, msg)
            if self.on_error:
                self.on_error(msg)
            return False

    def disconnect(self):
        """Disconnect and stop reader loop."""
        self._stop_event.set()
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=0.5)
            self._read_thread = None

        self._log("[INFO] Port serial ditutup.")
        if self.on_connection_state_changed:
            self.on_connection_state_changed(False, "Terputus dari Serial Port")

    def send_data(self, command: str) -> bool:
        """Send command string through serial port."""
        if self.is_connected and self._serial:
            try:
                if not command.endswith("\n"):
                    command += "\n"
                self._serial.write(command.encode("utf-8"))
                self._log(f"[TX SERIAL] {command.strip()}")
                return True
            except Exception as ex:
                if self.on_error:
                    self.on_error(f"Gagal kirim perintah serial: {ex}")
        return False

    def _reader_loop(self):
        """Background thread continuously reading lines from serial port."""
        while not self._stop_event.is_set() and self._serial and self._serial.is_open:
            try:
                if self._serial.in_waiting > 0:
                    raw_line = self._serial.readline().decode("utf-8", errors="ignore").strip()
                    if raw_line:
                        if self.on_raw_data_received:
                            self.on_raw_data_received(raw_line)

                        telemetry = DataParser.parse(raw_line)
                        if telemetry and self.on_telemetry_parsed:
                            self.on_telemetry_parsed(telemetry)
                else:
                    time.sleep(0.02)
            except (serial.SerialException, OSError) as ex:
                if not self._stop_event.is_set():
                    if self.on_error:
                        self.on_error(f"Serial port terputus: {ex}")
                    if self.on_connection_state_changed:
                        self.on_connection_state_changed(False, "Koneksi Serial terputus")
                break
            except Exception as ex:
                if self.on_error:
                    self.on_error(f"Error pembacaan serial: {ex}")
                time.sleep(0.05)

    def _log(self, text: str):
        if self.on_system_log:
            self.on_system_log(text)
