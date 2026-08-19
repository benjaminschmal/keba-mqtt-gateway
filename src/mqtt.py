from __future__ import annotations

import json
from typing import Any, Mapping

import paho.mqtt.client as mqtt

from .keba_modbus import KebaData


class MqttPublisher:
    """Publish KEBA state to MQTT. Discovery is intentionally separate."""

    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
        topic_prefix: str = "keba",
        client_id: str = "keba-mqtt-gateway",
    ) -> None:
        self.topic_prefix = topic_prefix.rstrip("/")
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
        if username:
            self.client.username_pw_set(username, password)
        self.client.connect(host, port, keepalive=60)

    def close(self) -> None:
        self.client.disconnect()

    def publish_data(self, data: KebaData, retain: bool = True) -> None:
        values: Mapping[str, Any] = {
            "charging_state": data.charging_state,
            "cable_state": data.cable_state,
            "error_code": data.error_code,
            "connected": data.connected,
            "charging": data.charging,
            "current_l1_a": data.current_l1_a,
            "current_l2_a": data.current_l2_a,
            "current_l3_a": data.current_l3_a,
            "active_power_w": data.active_power_w,
            "total_energy_kwh": data.total_energy_kwh,
            "voltage_l1_v": data.voltage_l1_v,
            "voltage_l2_v": data.voltage_l2_v,
            "voltage_l3_v": data.voltage_l3_v,
            "power_factor": data.power_factor,
            "max_current_a": data.max_current_a,
            "max_supported_current_a": data.max_supported_current_a,
            "session_energy_kwh": data.session_energy_kwh,
            "phase_switching_source": data.phase_switching_source,
            "phase_switching_state": data.phase_switching_state,
        }

        for name, value in values.items():
            self.client.publish(
                f"{self.topic_prefix}/{name}",
                json.dumps(value),
                qos=1,
                retain=retain,
            )

    def publish_availability(self, online: bool, retain: bool = True) -> None:
        self.client.publish(
            f"{self.topic_prefix}/availability",
            "online" if online else "offline",
            qos=1,
            retain=retain,
        )
