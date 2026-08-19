import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    evcc_host: str
    evcc_modbus_port: int = 1502
    evcc_unit_id: int = 255
    evcc_timeout: float = 3.0
    mqtt_host: str = ""
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    poll_interval: float = 5.0

    @classmethod
    def from_environment(cls) -> "GatewayConfig":
        evcc_host = os.getenv("EVCC_HOST")
        mqtt_host = os.getenv("MQTT_HOST")

        if not evcc_host:
            raise ValueError("EVCC_HOST environment variable is required.")

        if not mqtt_host:
            raise ValueError("MQTT_HOST environment variable is required.")

        return cls(
            evcc_host=evcc_host,
            evcc_modbus_port=int(os.getenv("EVCC_MODBUS_PORT", "1502")),
            evcc_unit_id=int(os.getenv("EVCC_UNIT_ID", "255")),
            evcc_timeout=float(os.getenv("EVCC_TIMEOUT", "3.0")),
            mqtt_host=mqtt_host,
            mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
            mqtt_username=os.getenv("MQTT_USERNAME", ""),
            mqtt_password=os.getenv("MQTT_PASSWORD", ""),
            poll_interval=float(os.getenv("POLL_INTERVAL", "5.0")),
        )
