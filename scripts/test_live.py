"""One-shot live test: EVCC Modbus proxy -> KEBA data -> MQTT."""

from __future__ import annotations

import os

from src.keba_modbus import KebaModbusClient
from src.mqtt import MqttPublisher


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing environment variable: {name}")
    return value


def main() -> None:
    evcc_host = os.getenv("EVCC_HOST", "192.168.1.10")
    evcc_port = int(os.getenv("EVCC_MODBUS_PORT", "1502"))
    mqtt_host = os.getenv("MQTT_HOST", "192.168.1.225")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_user = required("MQTT_USER")
    mqtt_password = required("MQTT_PASSWORD")

    modbus = KebaModbusClient(host=evcc_host, port=evcc_port)
    mqtt = None

    try:
        print(f"Connecting to EVCC proxy {evcc_host}:{evcc_port}...")
        if not modbus.connect():
            raise SystemExit("Could not connect to EVCC Modbus proxy")

        data = modbus.read_data()
        print("KEBA data read successfully:")
        print(f"  charging:          {data.charging}")
        print(f"  connected:         {data.connected}")
        print(f"  active power:      {data.active_power_w:.3f} W")
        print(f"  total energy:      {data.total_energy_kwh:.4f} kWh")
        print(f"  session energy:    {data.session_energy_kwh:.4f} kWh")
        print(f"  current L1/L2/L3:  {data.current_l1_a:.3f} / {data.current_l2_a:.3f} / {data.current_l3_a:.3f} A")

        print(f"Connecting to MQTT {mqtt_host}:{mqtt_port}...")
        mqtt = MqttPublisher(
            host=mqtt_host,
            port=mqtt_port,
            username=mqtt_user,
            password=mqtt_password,
        )
        mqtt.publish_availability(True)
        mqtt.publish_data(data)
        print("MQTT state published successfully.")
    finally:
        if mqtt is not None:
            mqtt.close()
        modbus.close()


if __name__ == "__main__":
    main()
