from src.keba_modbus import KebaData
from src.mqtt import MqttPublisher


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.published = []
        self.credentials = None

    def username_pw_set(self, username, password):
        self.credentials = (username, password)

    def connect(self, host, port, keepalive=60):
        self.connection = (host, port, keepalive)

    def disconnect(self):
        self.disconnected = True

    def publish(self, topic, payload, qos, retain):
        self.published.append((topic, payload, qos, retain))


def sample_data():
    return KebaData(
        charging_state=3,
        cable_state=7,
        error_code=0,
        current_l1_a=5.705,
        current_l2_a=5.754,
        current_l3_a=5.783,
        active_power_w=3798.395,
        total_energy_kwh=6626.9603,
        voltage_l1_v=228.0,
        voltage_l2_v=228.0,
        voltage_l3_v=227.0,
        power_factor=0.963,
        max_current_a=6.0,
        max_supported_current_a=32.0,
        session_energy_kwh=0.3055,
        phase_switching_source=3,
        phase_switching_state=1,
    )


def test_publish_data(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("src.mqtt.mqtt.Client", lambda *a, **kw: fake)

    publisher = MqttPublisher(
        host="mqtt.example",
        port=1883,
        username="user",
        password="secret",
        topic_prefix="keba",
    )
    publisher.publish_data(sample_data())

    assert fake.connection == ("mqtt.example", 1883, 60)
    assert fake.credentials == ("user", "secret")
    assert len(fake.published) == 19
    assert ("keba/charging", "true", 1, True) in fake.published
    assert ("keba/active_power_w", "3798.395", 1, True) in fake.published


def test_publish_availability(monkeypatch):
    fake = FakeClient()
    monkeypatch.setattr("src.mqtt.mqtt.Client", lambda *a, **kw: fake)

    publisher = MqttPublisher(host="mqtt.example")
    publisher.publish_availability(True)

    assert fake.published == [("keba/availability", "online", 1, True)]
