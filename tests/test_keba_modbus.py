import pytest

from src.keba_modbus import KebaModbusClient


def test_decode_uint32():
    assert KebaModbusClient.decode_uint32([0, 1]) == 1
    assert KebaModbusClient.decode_uint32([1011, 9677]) == 66266573


def test_decode_uint32_requires_two_words():
    with pytest.raises(ValueError):
        KebaModbusClient.decode_uint32([1])


def test_decode_live_verified_data():
    raw = {
        1000: 3,
        1004: 7,
        1006: 0,
        1008: 5705,
        1010: 5754,
        1012: 5783,
        1020: 3798395,
        1036: 66269603,
        1040: 228,
        1042: 228,
        1044: 227,
        1046: 963,
        1100: 6000,
        1110: 32000,
        1502: 3055,
        1550: 3,
        1552: 1,
    }

    data = KebaModbusClient.decode_data(raw)

    assert data.charging_state == 3
    assert data.cable_state == 7
    assert data.error_code == 0
    assert data.current_l1_a == pytest.approx(5.705)
    assert data.current_l2_a == pytest.approx(5.754)
    assert data.current_l3_a == pytest.approx(5.783)
    assert data.active_power_w == pytest.approx(3798.395)
    assert data.total_energy_kwh == pytest.approx(6626.9603)
    assert data.voltage_l1_v == 228
    assert data.voltage_l2_v == 228
    assert data.voltage_l3_v == 227
    assert data.power_factor == pytest.approx(0.963)
    assert data.max_current_a == pytest.approx(6.0)
    assert data.max_supported_current_a == pytest.approx(32.0)
    assert data.session_energy_kwh == pytest.approx(0.3055)
    assert data.phase_switching_source == 3
    assert data.phase_switching_state == 1
    assert data.connected is True
    assert data.charging is True
