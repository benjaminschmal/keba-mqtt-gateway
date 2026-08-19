from dataclasses import dataclass
from typing import Dict, List

from pymodbus.client import ModbusTcpClient


UNIT_ID = 255


@dataclass(frozen=True)
class KebaData:
    charging_state: int
    cable_state: int
    error_code: int
    current_l1_a: float
    current_l2_a: float
    current_l3_a: float
    active_power_w: float
    total_energy_kwh: float
    voltage_l1_v: float
    voltage_l2_v: float
    voltage_l3_v: float
    power_factor: float
    max_current_a: float
    max_supported_current_a: float
    session_energy_kwh: float
    phase_switching_state: int

    @property
    def connected(self) -> bool:
        return self.cable_state in (5, 7)

    @property
    def charging(self) -> bool:
        return self.charging_state == 3


class KebaModbusClient:
    """Read-only Modbus client for a KEBA P30 via the EVCC proxy."""

    def __init__(
        self,
        host: str,
        port: int = 1502,
        unit_id: int = UNIT_ID,
        timeout: float = 3.0,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.client = ModbusTcpClient(
            host=self.host,
            port=self.port,
            timeout=self.timeout,
        )

    def connect(self) -> bool:
        return self.client.connect()

    def close(self) -> None:
        self.client.close()

    def read_uint32(self, address: int) -> int:
        """Read one KEBA UINT32 register using FC3.

        KEBA exposes each readable value as a UINT32, therefore exactly
        two Modbus words are requested per register.
        """
        response = self.client.read_holding_registers(
            address=address,
            count=2,
            slave=self.unit_id,
        )

        if response.isError():
            raise RuntimeError(
                f"Modbus read failed for register {address}: {response}"
            )

        if len(response.registers) != 2:
            raise RuntimeError(
                f"Unexpected register count for {address}: "
                f"{len(response.registers)}"
            )

        return (response.registers[0] << 16) | response.registers[1]

    def read_data(self) -> KebaData:
        """Read the core read-only KEBA data set."""
        raw: Dict[int, int] = {
            address: self.read_uint32(address)
            for address in (
                1000,
                1004,
                1006,
                1008,
                1010,
                1012,
                1020,
                1036,
                1040,
                1042,
                1044,
                1046,
                1100,
                1110,
                1502,
                1552,
            )
        }

        return KebaData(
            charging_state=raw[1000],
            cable_state=raw[1004],
            error_code=raw[1006],
            current_l1_a=raw[1008] / 1000.0,
            current_l2_a=raw[1010] / 1000.0,
            current_l3_a=raw[1012] / 1000.0,
            active_power_w=raw[1020] / 1000.0,
            total_energy_kwh=raw[1036] / 10000.0,
            voltage_l1_v=float(raw[1040]),
            voltage_l2_v=float(raw[1042]),
            voltage_l3_v=float(raw[1044]),
            power_factor=raw[1046] / 1000.0,
            max_current_a=raw[1100] / 1000.0,
            max_supported_current_a=raw[1110] / 1000.0,
            session_energy_kwh=raw[1502] / 10000.0,
            phase_switching_state=raw[1552],
        )

    @staticmethod
    def decode_uint32(registers: List[int]) -> int:
        if len(registers) != 2:
            raise ValueError("A KEBA UINT32 requires exactly two registers")
        return (registers[0] << 16) | registers[1]
