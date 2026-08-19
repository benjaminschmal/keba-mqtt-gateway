from __future__ import annotations

import os
import threading
import time
from typing import Callable

from .keba_modbus import KebaData, KebaModbusClient
from .mqtt import MqttPublisher
from .web import WebState, create_app


class Gateway:
    """Run the read-only KEBA -> MQTT gateway and update web status."""

    def __init__(self) -> None:
        self.evcc_host = os.getenv("EVCC_HOST", "192.168.1.10")
        self.evcc_port = int(os.getenv("EVCC_MODBUS_PORT", "1502"))
        self.mqtt_host = os.getenv("MQTT_HOST", "192.168.1.225")
        self.mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        self.mqtt_user = os.getenv("MQTT_USER", "mqtt")
        self.mqtt_password = os.getenv("MQTT_PASSWORD")
        self.web_host = os.getenv("WEB_HOST", "0.0.0.0")
        self.web_port = int(os.getenv("WEB_PORT", "8080"))
        self.poll_interval = max(float(os.getenv("POLL_INTERVAL", "2.0")), 0.6)
        self.state = WebState()
        self.modbus = KebaModbusClient(self.evcc_host, self.evcc_port)
        self.mqtt: MqttPublisher | None = None
        self._stop = threading.Event()

    def _publish(self, data: KebaData) -> None:
        if self.mqtt is None:
            return
        self.mqtt.publish_availability(True)
        self.mqtt.publish_data(data)
        self.state.update(mqtt_connected=True)

    def run(self) -> None:
        if not self.mqtt_password:
            raise RuntimeError("MQTT_PASSWORD is required")

        self.mqtt = MqttPublisher(
            self.mqtt_host,
            self.mqtt_port,
            self.mqtt_user,
            self.mqtt_password,
        )

        while not self._stop.is_set():
            try:
                if not self.modbus.client.is_socket_open():
                    self.modbus.connect()

                data = self.modbus.read_data()
                self.state.update(
                    modbus_connected=True,
                    mqtt_connected=True,
                    charging=data.charging,
                    connected=data.connected,
                    charging_state=data.charging_state,
                    cable_state=data.cable_state,
                    error_code=data.error_code,
                    current_l1_a=data.current_l1_a,
                    current_l2_a=data.current_l2_a,
                    current_l3_a=data.current_l3_a,
                    active_power_w=data.active_power_w,
                    total_energy_kwh=data.total_energy_kwh,
                    voltage_l1_v=data.voltage_l1_v,
                    voltage_l2_v=data.voltage_l2_v,
                    voltage_l3_v=data.voltage_l3_v,
                    power_factor=data.power_factor,
                    max_current_a=data.max_current_a,
                    max_supported_current_a=data.max_supported_current_a,
                    session_energy_kwh=data.session_energy_kwh,
                    phase_switching_source=data.phase_switching_source,
                    phase_switching_state=data.phase_switching_state,
                )
                self._publish(data)
            except Exception as exc:
                self.state.update(
                    modbus_connected=self.modbus.client.is_socket_open(),
                    mqtt_connected=False,
                    last_error=str(exc),
                )
            self._stop.wait(self.poll_interval)

    def stop(self) -> None:
        self._stop.set()
        if self.mqtt is not None:
            self.mqtt.publish_availability(False)
            self.mqtt.close()
        self.modbus.close()


def main() -> None:
    gateway = Gateway()
    app = create_app(gateway.state)
    web_thread = threading.Thread(
        target=lambda: app.run(
            host=gateway.web_host,
            port=gateway.web_port,
            debug=False,
            use_reloader=False,
        ),
        daemon=True,
    )
    web_thread.start()

    try:
        gateway.run()
    except KeyboardInterrupt:
        pass
    finally:
        gateway.stop()


if __name__ == "__main__":
    main()
