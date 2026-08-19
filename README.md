# KEBA MQTT Gateway

Read-only MQTT gateway for a KEBA KeContact P30 X-Series.

The gateway reads KEBA data through the EVCC Modbus TCP proxy and publishes the values via MQTT, including Home Assistant MQTT Discovery.

## Architecture

```text
KEBA P30 X-Series
        |
        | Modbus TCP
        v
      EVCC
        |
        | Modbus TCP Proxy (read-only)
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

The gateway never connects directly to the KEBA wallbox. EVCC remains the only direct Modbus client of the KEBA. The gateway uses the EVCC Modbus proxy exclusively and performs read operations only.

## Development status

Project initialization. Register mapping, MQTT topics and Home Assistant Discovery entities will be added after the KEBA register set has been verified through the EVCC proxy.

## Configuration

Configuration will use environment variables. No local network addresses, credentials or other private configuration values are stored in the repository.
