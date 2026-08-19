import os

import pytest

from src.config import GatewayConfig


def test_config_from_environment(monkeypatch):
    monkeypatch.setenv("EVCC_HOST", "evcc.example")
    monkeypatch.setenv("MQTT_HOST", "mqtt.example")

    config = GatewayConfig.from_environment()

    assert config.evcc_host == "evcc.example"
    assert config.evcc_modbus_port == 1502
    assert config.evcc_unit_id == 255
    assert config.mqtt_host == "mqtt.example"
    assert config.mqtt_port == 1883
    assert config.poll_interval == 5.0


def test_config_requires_evcc_host(monkeypatch):
    monkeypatch.delenv("EVCC_HOST", raising=False)
    monkeypatch.setenv("MQTT_HOST", "mqtt.example")

    with pytest.raises(ValueError, match="EVCC_HOST"):
        GatewayConfig.from_environment()


def test_config_requires_mqtt_host(monkeypatch):
    monkeypatch.setenv("EVCC_HOST", "evcc.example")
    monkeypatch.delenv("MQTT_HOST", raising=False)

    with pytest.raises(ValueError, match="MQTT_HOST"):
        GatewayConfig.from_environment()
