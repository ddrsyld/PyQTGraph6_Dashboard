"""
MQTT Service for BMS Dashboard using Paho MQTT
Supports HiveMQ Cloud, Public HiveMQ Broker, EMQX, and Mosquitto.
Includes dual subscription, connection health tracking, and debug logging.
"""

import threading
import uuid
from typing import Callable, Optional
import paho.mqtt.client as mqtt

from models.telemetry import BatteryTelemetry
from services.data_parser import DataParser


class MqttService:
    def __init__(self):
        self._client: Optional[mqtt.Client] = None
        self._is_connected = False
        self.current_broker = "broker.emqx.io"
        self.current_port = 1883
        self.current_topic = "sic/bms/telemetry"

        # Callbacks
        self.on_raw_data_received: Optional[Callable[[str], None]] = None
        self.on_telemetry_parsed: Optional[Callable[[BatteryTelemetry], None]] = None
        self.on_connection_state_changed: Optional[Callable[[bool, str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_system_log: Optional[Callable[[str], None]] = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected and self._client is not None

    def connect(self, broker: str = "broker.emqx.io", port: int = 1883,
                topic: str = "sic/bms/telemetry",
                username: Optional[str] = None, password: Optional[str] = None,
                client_id: Optional[str] = None) -> bool:
        """Connect to MQTT broker and start network loop thread."""
        try:
            self.disconnect()

            self.current_broker = broker.strip() if broker else "broker.emqx.io"
            self.current_port = int(port)
            self.current_topic = topic.strip() if topic else "sic/bms/telemetry"

            if not client_id:
                client_id = f"BMS_Py_{uuid.uuid4().hex[:6]}"

            # Paho MQTT 2.0+ API check
            try:
                self._client = mqtt.Client(
                    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                    client_id=client_id
                )
            except (AttributeError, TypeError):
                self._client = mqtt.Client(client_id=client_id)

            if username and password:
                self._client.username_pw_set(username, password)

            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_message = self._on_message

            self._log(f"Menghubungkan ke broker: {self.current_broker}:{self.current_port}...")
            self._client.connect_async(self.current_broker, self.current_port, keepalive=60)
            self._client.loop_start()

            if self.on_connection_state_changed:
                self.on_connection_state_changed(False, f"Menghubungkan ke {self.current_broker}...")
            return True

        except Exception as e:
            msg = f"Gagal inisialisasi MQTT: {str(e)}"
            self._log(f"[ERROR] {msg}")
            if self.on_connection_state_changed:
                self.on_connection_state_changed(False, msg)
            if self.on_error:
                self.on_error(msg)
            return False

    def disconnect(self):
        """Disconnect and stop network loop."""
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
            self._client = None
            self._is_connected = False
            self._log("Koneksi MQTT dihentikan.")
            if self.on_connection_state_changed:
                self.on_connection_state_changed(False, "Terputus dari Broker MQTT")

    def publish(self, topic: str, payload: str, qos: int = 0) -> bool:
        """Publish control message/command to MQTT topic."""
        if self._client and self._is_connected:
            try:
                self._client.publish(topic, payload, qos=qos)
                self._log(f"[TX MQTT] Topic: {topic} | Payload: {payload}")
                return True
            except Exception as ex:
                if self.on_error:
                    self.on_error(f"Gagal publish MQTT: {ex}")
        return False

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        rc = reason_code if isinstance(reason_code, int) else getattr(reason_code, "value", 0)
        if rc == 0:
            self._is_connected = True
            # Subscribe to main topic and wildcard topic to catch all BMS streams
            client.subscribe([(self.current_topic, 0), ("sic/bms/#", 0)])
            self._log(f"[OK] Terhubung ke Broker: {self.current_broker}:{self.current_port}")
            self._log(f"[OK] Subscribed ke topik: '{self.current_topic}' dan 'sic/bms/#'")
            self._log("[INFO] Menunggu data dari Wokwi/ESP32... (Pastikan Wokwi sedang RUNNING)")

            if self.on_connection_state_changed:
                self.on_connection_state_changed(
                    True,
                    f"BROKER TERHUBUNG | MENUNGGU DATA DARI ESP32 ({self.current_broker})"
                )
        else:
            self._is_connected = False
            msg = f"Koneksi broker ditolak (Kode: {reason_code})"
            self._log(f"[ERROR] {msg}")
            if self.on_connection_state_changed:
                self.on_connection_state_changed(False, msg)
            if self.on_error:
                self.on_error(msg)

    def _on_disconnect(self, client, userdata, *args):
        self._is_connected = False
        self._log("[INFO] Terputus dari broker MQTT.")
        if self.on_connection_state_changed:
            self.on_connection_state_changed(False, "Koneksi MQTT terputus.")

    def _on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8", errors="ignore").strip()
            if payload_str:
                if self.on_raw_data_received:
                    self.on_raw_data_received(payload_str)

                telemetry = DataParser.parse(payload_str)
                if telemetry and self.on_telemetry_parsed:
                    self.on_telemetry_parsed(telemetry)
        except Exception as e:
            if self.on_error:
                self.on_error(f"Error proses pesan MQTT: {e}")

    def _log(self, text: str):
        if self.on_system_log:
            self.on_system_log(text)
