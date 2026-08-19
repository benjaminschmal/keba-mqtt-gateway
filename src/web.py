from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any

from flask import Flask, jsonify, render_template_string


HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KEBA MQTT Gateway</title>
<style>
body { font-family: system-ui, sans-serif; margin: 2rem; max-width: 1100px; }
h1 { margin-bottom: .25rem; }
small { color: #666; }
.grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 1rem; margin-top: 1.5rem; }
.card { border: 1px solid #ddd; border-radius: 10px; padding: 1rem; }
.value { font-size: 1.6rem; font-weight: 600; margin-top: .4rem; }
.ok { color: #188038; } .bad { color: #b3261e; }
</style>
</head>
<body>
<h1>KEBA MQTT Gateway</h1>
<small id="updated">Waiting for data...</small>
<div class="grid" id="cards"></div>
<script>
async function refresh() {
  const response = await fetch('/api/status', {cache: 'no-store'});
  const data = await response.json();
  document.getElementById('updated').textContent = 'Updated: ' + (data.timestamp || 'n/a');
  const values = [
    ['Modbus', data.modbus_connected ? 'Connected' : 'Disconnected'],
    ['MQTT', data.mqtt_connected ? 'Connected' : 'Disconnected'],
    ['Charging', data.charging ? 'Yes' : 'No'],
    ['Connected', data.connected ? 'Yes' : 'No'],
    ['Active Power', (data.active_power_w ?? 0).toFixed(1) + ' W'],
    ['Total Energy', (data.total_energy_kwh ?? 0).toFixed(4) + ' kWh'],
    ['Session Energy', (data.session_energy_kwh ?? 0).toFixed(4) + ' kWh'],
    ['Current L1/L2/L3', `${(data.current_l1_a ?? 0).toFixed(2)} / ${(data.current_l2_a ?? 0).toFixed(2)} / ${(data.current_l3_a ?? 0).toFixed(2)} A`],
    ['Voltage L1/L2/L3', `${data.voltage_l1_v ?? 0} / ${data.voltage_l2_v ?? 0} / ${data.voltage_l3_v ?? 0} V`],
    ['Power Factor', ((data.power_factor ?? 0) * 100).toFixed(1) + ' %'],
    ['Error Code', data.error_code ?? 'n/a'],
  ];
  document.getElementById('cards').innerHTML = values.map(([name,value]) => `<div class="card"><div>${name}</div><div class="value">${value}</div></div>`).join('');
}
refresh();
setInterval(refresh, 2000);
</script>
</body>
</html>
"""


class WebState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._data: dict[str, Any] = {
            "timestamp": None,
            "modbus_connected": False,
            "mqtt_connected": False,
        }

    def update(self, **values: Any) -> None:
        with self._lock:
            self._data.update(values)
            self._data["timestamp"] = datetime.now(timezone.utc).isoformat()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._data)


def create_app(state: WebState | None = None) -> Flask:
    state = state or WebState()
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template_string(HTML)

    @app.get("/api/status")
    def api_status():
        return jsonify(state.snapshot())

    @app.get("/health")
    def health():
        data = state.snapshot()
        ok = bool(data.get("modbus_connected") and data.get("mqtt_connected"))
        return jsonify({"status": "ok" if ok else "degraded", **data}), 200 if ok else 503

    return app
