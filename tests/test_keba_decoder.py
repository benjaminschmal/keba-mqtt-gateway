import pytest

from src.keba_modbus import KebaModbusClient


# Example values taken from the KEBA P30 Modbus TCP Programmers Guide V1.07.
FIXTURE = {
    1000: 3,
    1004: 7,
    1006: 0,
    1008: 645,
    1010: 1011,
    1012: 645,
    1020: 98661,
    1036: 38101,
    1040: 230,
    1042: 230,
    1044: 230,
    1046: 928,
    1100: 10000,
    1110: 10000,
    1502: 165,
    1550: 3,
    1552: 3,
}


def test_decode_keba_data():
    data = KebaModbusClient.decode_data(FIXTURE)

    assert data.charging_state == 3
    assert data.cable_state == 7
    assert data.error_code == 0

    assert data.current_l1_a == pytest.approx(0.645)
    assert data.current_l2_a == pytest.approx(1.011)
    assert data.current_l3_a == pytest.approx(0.645)

    assert data.active_power_w == pytest.approx(98.661)
    assert data.total_energy_kwh == pytest.approx(3.8101)

    assert data.voltage_l1_v == pytest.approx(230)
    assert data.voltage_l2_v == pytest.approx(230)
    assert data.voltage_l3_v == pytest.approx(230)
    assert data.power_factor == pytest.approx(0.928)

    assert data.max_current_a == pytest.approx(10.0)
    assert data.max_supported_current_a == pytest.approx(10.0)
    assert data.session_energy_kwh == pytest.approx(0.0165)
    assert data.phase_switching_source == 3
    assert data.phase_switching_state == 3

    assert data.connected is True
    assert data.charging is True


def test_decode_uint32():
    assert KebaModbusClient.decode_uint32([0, 1]) == 1
    assert KebaModbusClient.decode_uint32([1, 0]) == 65536


def test_decode_uint32_requires_two_words():
    with pytest.raises(ValueError):
        KebaModbusClient.decode_uint32([1])
