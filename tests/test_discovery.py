import json

from src.keba_modbus import KebaData
from src.mqtt import MqttPublisher


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.published = []

    def username_pw_set(self, username, password):
        pass

    def connect(self, host, port, keepalive=60):
        pass

    def loop_start(self):
        pass

    def loop_stop(self):
        pass

    def disconnect(self):
        pass

    def publish(self, topic, payload, qos, retain):
        self.published.append((topic, payload, qos, retain))


def test_publish_discovery(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("src.mqtt.mqtt.Client", lambda *a, **kw: fake)

    publisher = MqttPublisher(host="mqtt.example", topic_prefix="keba")
    publisher.publish_discovery()

    assert len(fake.published) == 19

    topic, payload, qos, retain = fake.published[0]
    config = json.loads(payload)
    assert topic == "homeassistant/binary_sensor/keba_p30/connected/config"
    assert config["unique_id"] == "keba_p30_connected"
    assert config["state_topic"] == "keba/connected"
    assert config["device"]["identifiers"] == ["keba_p30"]
    assert config["availability"]["topic"] == "keba/availability"
    assert qos == 1
    assert retain is True


def test_discovery_uses_expected_energy_metadata(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("src.mqtt.mqtt.Client", lambda *a, **kw: fake)

    publisher = MqttPublisher(host="mqtt.example")
    publisher.publish_discovery()

    messages = {topic: json.loads(payload) for topic, payload, _, _ in fake.published}
    total = messages["homeassistant/sensor/keba_p30/total_energy_kwh/config"]
    assert total["device_class"] == "energy"
    assert total["state_class"] == "total_increasing"
    assert total["unit_of_measurement"] == "kWh"
