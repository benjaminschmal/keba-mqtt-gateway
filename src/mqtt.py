from __future__ import annotations

import json
from typing import Any, Mapping

import paho.mqtt.client as mqtt

from .keba_modbus import KebaData


class MqttPublisher:
    """Publish KEBA state and Home Assistant MQTT Discovery messages."""

    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: str | None = None,
        password: str | None = None,
        topic_prefix: str = "keba",
        client_id: str = "keba-mqtt-gateway",
        discovery_prefix: str = "homeassistant",
    ) -> None:
        self.topic_prefix = topic_prefix.rstrip("/")
        self.discovery_prefix = discovery_prefix.rstrip("/")
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
        if username:
            self.client.username_pw_set(username, password)
        self.client.connect(host, port, keepalive=60)
        self.client.loop_start()

    def close(self) -> None:
        self.client.loop_stop()
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

    def publish_discovery(self, retain: bool = True) -> None:
        """Publish Home Assistant MQTT Discovery configuration for the KEBA device."""
        device = {
            "identifiers": ["keba_p30"],
            "name": "KEBA P30",
            "manufacturer": "KEBA",
            "model": "P30 X-Series",
        }
        availability = {
            "topic": f"{self.topic_prefix}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
        }

        entities = [
            ("binary_sensor", "connected", "Connected", "mdi:ev-plug-type2", {"payload_on": "true", "payload_off": "false"}),
            ("binary_sensor", "charging", "Charging", "mdi:ev-station", {"payload_on": "true", "payload_off": "false"}),
            ("sensor", "active_power_w", "Active Power", "mdi:flash", {"device_class": "power", "state_class": "measurement", "unit_of_measurement": "W"}),
            ("sensor", "total_energy_kwh", "Total Energy", "mdi:counter", {"device_class": "energy", "state_class": "total_increasing", "unit_of_measurement": "kWh"}),
            ("sensor", "session_energy_kwh", "Session Energy", "mdi:lightning-bolt", {"device_class": "energy", "state_class": "measurement", "unit_of_measurement": "kWh"}),
            ("sensor", "current_l1_a", "Current L1", "mdi:current-ac", {"device_class": "current", "state_class": "measurement", "unit_of_measurement": "A"}),
            ("sensor", "current_l2_a", "Current L2", "mdi:current-ac", {"device_class": "current", "state_class": "measurement", "unit_of_measurement": "A"}),
            ("sensor", "current_l3_a", "Current L3", "mdi:current-ac", {"device_class": "current", "state_class": "measurement", "unit_of_measurement": "A"}),
            ("sensor", "voltage_l1_v", "Voltage L1", "mdi:sine-wave", {"device_class": "voltage", "state_class": "measurement", "unit_of_measurement": "V"}),
            ("sensor", "voltage_l2_v", "Voltage L2", "mdi:sine-wave", {"device_class": "voltage", "state_class": "measurement", "unit_of_measurement": "V"}),
            ("sensor", "voltage_l3_v", "Voltage L3", "mdi:sine-wave", {"device_class": "voltage", "state_class": "measurement", "unit_of_measurement": "V"}),
            ("sensor", "power_factor", "Power Factor", "mdi:cosine-wave", {"state_class": "measurement", "entity_category": "diagnostic"}),
            ("sensor", "max_current_a", "Max Charging Current", "mdi:current-ac", {"device_class": "current", "state_class": "measurement", "unit_of_measurement": "A"}),
            ("sensor", "max_supported_current_a", "Max Supported Current", "mdi:current-ac", {"device_class": "current", "state_class": "measurement", "unit_of_measurement": "A", "entity_category": "diagnostic"}),
            ("sensor", "error_code", "Error Code", "mdi:alert-circle-outline", {"entity_category": "diagnostic"}),
            ("sensor", "charging_state", "Charging State", "mdi:ev-station", {"entity_category": "diagnostic"}),
            ("sensor", "cable_state", "Cable State", "mdi:connection", {"entity_category": "diagnostic"}),
            ("sensor", "phase_switching_source", "Phase Switching Source", "mdi:swap-horizontal", {"entity_category": "diagnostic"}),
            ("sensor", "phase_switching_state", "Phase Switching State", "mdi:swap-horizontal", {"entity_category": "diagnostic"}),
        ]

        for component, key, name, icon, extra in entities:
            config: dict[str, Any] = {
                "name": name,
                "unique_id": f"keba_p30_{key}",
                "state_topic": f"{self.topic_prefix}/{key}",
                "availability": availability,
                "device": device,
                "icon": icon,
                **extra,
            }
            topic = f"{self.discovery_prefix}/{component}/keba_p30/{key}/config"
            self.client.publish(topic, json.dumps(config), qos=1, retain=retain)
