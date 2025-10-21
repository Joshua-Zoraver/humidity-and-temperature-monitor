# main.py

import time
import socket
import requests
from src.sensors import SensorReader
from src.thresholds import process_sensor_reading
from src import shared_state
from src.GPIO_environment_control import apply_environment_control, shutdown_devices
from src.sensor_db import init_db

try:
    from src import lights
    USE_LIGHTS = True
except ImportError:
    print("[main] lights.py not found, skipping LED matrix display")
    USE_LIGHTS = False

# ----------------------------
# Configuration
# ----------------------------
SERVER_URL = "http://192.168.86.20:5000/submit-data"  # Replace with Flask server IP

def get_pi_id():
    """
    Generates a unique Pi ID using hostname and last octet of local IP.
    """
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
        last_octet = ip_address.split('.')[-1]
        pi_id = f"pi-{last_octet}"
    except Exception:
        pi_id = hostname
    return pi_id

PI_ID = get_pi_id()
print(f"[main] Pi ID set to: {PI_ID}")

# ----------------------------
# Helper functions
# ----------------------------
def send_to_server(result):
    payload = result.copy()
    payload["pi_id"] = PI_ID
    try:
        resp = requests.post(SERVER_URL, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to send data to server: {e}")

def handle_sensor_data(sensor_data):
    shared_state.latest_data = sensor_data
    results = process_sensor_reading(sensor_data)

    control_actions = apply_environment_control(sensor_data)
    print("[GPIO CONTROL]", control_actions)

    if USE_LIGHTS:
        lights.update_display(sensor_data)

    for r in results:
        print(f"{r['timestamp']} | {r['sensor']}: {r['value']} -> {r['status']}")
        send_to_server(r)

# ----------------------------
# Main
# ----------------------------
def main():
    init_db()
    print("[main] Starting SensorReader")

    if USE_LIGHTS:
        lights.init_joystick()

    reader = SensorReader(interval=10, callback=handle_sensor_data)
    reader.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[main] Stopping...")
        reader.stop()
        reader.join()

        if USE_LIGHTS:
            lights.clear()

        shutdown_devices()
        print("[main] Shutdown complete.")

if __name__ == "__main__":
    main()
