# KEBA P30 X-Series – Technical Findings

Status: verified during live testing on 2026-08-19

## Scope

The gateway reads the KEBA P30 X-Series **only through the EVCC Modbus TCP proxy**. It does not connect directly to the KEBA.

```text
KEBA P30 X-Series
        |
        | Modbus TCP
        v
      EVCC
        |
        | Modbus TCP Proxy, read-only
        v
KEBA MQTT Gateway
        |
        | MQTT
        v
    Mosquitto
        |
        v
 Home Assistant
```

The direct KEBA connection is already used by EVCC. Parallel direct Modbus access from another client was found to be problematic in the target setup, therefore the EVCC proxy is the only supported data path for this project.

## EVCC proxy

The development/test setup uses an EVCC Modbus TCP proxy. The gateway connects to the proxy and sends Modbus read requests with KEBA Unit ID `255`.

The proxy is configured as read-only and rejects write operations. The gateway itself contains no Modbus write functionality.

No local IP addresses, hostnames, credentials or other private network information are stored in this document.

## Communication verification

The complete path was successfully tested from a Mac using PyModbus 3.8.6:

- TCP connection to the EVCC proxy: successful
- Modbus TCP connection: successful
- Unit ID: `255`
- Function code: FC3 / Read Holding Registers
- Reading two registers per UINT32 value: successful
- Live data returned by the KEBA through the EVCC proxy: verified

The KEBA documentation specifies the readable values as `UINT32`; the implementation therefore requests exactly two Modbus words per register.

## Verified register mapping

| Register | Name | Type | Unit / scaling | Live verification |
|---:|---|---|---|---|
| `1000` | Charging State | UINT32 | enum | `1` idle/not ready, `3` charging |
| `1004` | Cable State | UINT32 | enum | `3` idle/locked, `7` connected and locked while charging |
| `1006` | Error Code | UINT32 | code | `0` during both tests |
| `1008` | Current L1 | UINT32 | mA | address verified; live value not yet included in test output |
| `1010` | Current L2 | UINT32 | mA | address verified; live value not yet included in test output |
| `1012` | Current L3 | UINT32 | mA | address verified; live value not yet included in test output |
| `1020` | Active Power | UINT32 | mW | `3,798,395` => `3,798.395 W` while charging |
| `1036` | Total Energy | UINT32 | 0.1 Wh | `66,266,573` => `6,626.6573 kWh`; later `66,269,603` => `6,626.9603 kWh` |
| `1040` | Voltage L1 | UINT32 | V | `0` idle; `228 V` charging |
| `1042` | Voltage L2 | UINT32 | V | `0` idle; `228 V` charging |
| `1044` | Voltage L3 | UINT32 | V | `0` idle; `227 V` charging |
| `1046` | Power Factor | UINT32 | 0.1 % | address verified; live value not yet included in test output |
| `1100` | Max Charging Current | UINT32 | mA | address verified; live value not yet included in test output |
| `1110` | Max Supported Current | UINT32 | mA | address verified; live value not yet included in test output |
| `1502` | Charged Energy / Session Energy | UINT32 | 0.1 Wh | `1,653` => `0.1653 kWh` idle test; `3,055` => `0.3055 kWh` charging test |
| `1550` | Phase Switching Source | UINT32 | enum | `3` in both tests |
| `1552` | Phase Switching State | UINT32 | enum | `0` idle; `1` while charging |

## Live test snapshots

### Idle / not charging

Observed values:

```text
1000  Charging State        = 1
1004  Cable State           = 3
1006  Error Code            = 0
1020  Active Power          = 0 mW
1036  Total Energy          = 66,266,573 (0.1 Wh)
1040  Voltage L1            = 0 V
1042  Voltage L2            = 0 V
1044  Voltage L3            = 0 V
1502  Session Energy        = 1,653 (0.1 Wh)
1550  Phase Switching Source= 3
1552  Phase Switching State = 0
```

### Charging

Observed values:

```text
1000  Charging State        = 3
1004  Cable State           = 7
1006  Error Code            = 0
1020  Active Power          = 3,798,395 mW = 3,798.395 W
1036  Total Energy          = 66,269,603 (0.1 Wh)
1040  Voltage L1            = 228 V
1042  Voltage L2            = 228 V
1044  Voltage L3            = 227 V
1502  Session Energy        = 3,055 (0.1 Wh)
1550  Phase Switching Source= 3
1552  Phase Switching State = 1
```

The increase of register `1036` between the two snapshots was `3,030` units = `303 Wh`, which is consistent with the observed charging period and confirms the documented `0.1 Wh` scaling.

## State interpretation

The KEBA documentation defines charging state `3` as an active charging process. Cable state `7` means the cable is connected to the charging station and the vehicle and is locked while charging.

For the gateway, the initial state model will therefore expose at least:

- `charging_state`
- `cable_state`
- `error_code`
- `connected`
- `charging`

`charging` can be derived from charging state `3`. `connected` should be derived from the cable state rather than from power alone.

## Polling requirements

KEBA documentation recommends more than 0.5 seconds between register reads. The gateway will therefore use a configurable polling interval and will not poll faster than the documented limit.

## Data still to verify

The following addresses are documented and already part of the planned data model, but their current live values have not yet been captured in the test output:

- `1008`, `1010`, `1012` – phase currents
- `1046` – power factor
- `1100` – maximum charging current
- `1110` – maximum supported current

These should be live-verified before the MQTT/Home Assistant entity model is finalized.

## Source documentation

KEBA currently lists the **Modbus TCP Programmers Guide V1.07** in its official eMobility downloads. The V1.07 document records the correction of registers `1036` and `1502` to unit `0.1 Wh` in version 1.06 and documents the readable registers used above.
