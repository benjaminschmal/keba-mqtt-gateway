# KEBA MQTT Gateway

Read-only MQTT gateway for a KEBA KeContact P30 X-Series.

The gateway reads KEBA data through the EVCC Modbus TCP proxy and publishes the values via MQTT, including Home Assistant MQTT Discovery. A lightweight web interface provides live status and diagnostics.

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
   |            |
   | MQTT       | HTTP :8080
   v            v
Mosquitto    Web UI / health
   |
   v
Home Assistant
```

The gateway never connects directly to the KEBA wallbox. EVCC remains the only direct Modbus client of the KEBA. The gateway uses the EVCC Modbus proxy exclusively and performs read operations only.

## Features

- Read-only KEBA P30 data through EVCC Modbus TCP proxy
- MQTT state publishing with retained QoS 1 messages
- Home Assistant MQTT Discovery
- MQTT availability state
- Live web UI at port `8080`
- `/api/status` JSON endpoint
- `/health` health endpoint
- Docker support
- Automated tests for decoding and MQTT behavior

## Verified data

The currently verified register set includes charging/cable state, error code, phase currents, active power, total energy, phase voltages, power factor, current limits, session energy and phase switching information.

## Configuration

Configuration is provided through environment variables. Use `.env.example` as a template. Never commit credentials or other secrets.

Important variables include:

```text
EVCC_HOST
EVCC_MODBUS_PORT
EVCC_UNIT_ID
EVCC_TIMEOUT
MQTT_HOST
MQTT_PORT
MQTT_USER
MQTT_PASSWORD
POLL_INTERVAL
WEB_HOST
WEB_PORT
```

The default examples should be replaced with values appropriate for the local installation.

## Development

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run tests:

```bash
python3 -m pytest -q
```

Run locally:

```bash
export MQTT_USER='mqtt'
export MQTT_PASSWORD='your-password'
python3 -m src.gateway
```

Open `http://localhost:8080` for the live monitoring page.

## Docker

The container exposes port `8080` for the web interface. Pass the MQTT credentials and EVCC proxy settings as environment variables. The container is intended for a trusted local network.

## Security

Do not expose the web interface or MQTT broker directly to the Internet. See [SECURITY.md](SECURITY.md) for the security policy.
