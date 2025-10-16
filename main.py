import time
from src.sensors import SensorReader
from src.thresholds import process_sensor_reading
from src import shared_state
from src.sensor_db import init_db

try:
    from src import lights
    USE_LIGHTS = True
except ImportError:
    print("[main] lights.py not found, skipping LED matrix display")
    USE_LIGHTS = False

def handle_sensor_data(sensor_data):
    #This function is called automatically by SensorReader after each reading
    #It processes the data through thresholds and optionally updates display

    #Cache latest data for joystick refresh
    shared_state.latest_data = sensor_data

    #Evaluate sensor values and thresholds
    results = process_sensor_reading(sensor_data)

    #Update LED if applicable
    if USE_LIGHTS:
        lights.update_display(sensor_data)


    #Debugging results
    for r in results:
        print(f"{r['timestamp']} | {r['sensor']}: {r['value']} -> {r['status']}")

def main():
    init_db()
    print("[main] Starting SensorReader")

    #Initialize joystick if using lights
    if USE_LIGHTS:
        lights.init_joystick()

    #Create and start background reader
    reader = SensorReader(interval=10, callback=handle_sensor_data)
    reader.start()

    try:
        #Keep program alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[main] Stopping...")
        reader.stop()
        reader.join()

        if USE_LIGHTS:
            lights.clear()
        print("[main] Shutdown complete.")

if __name__ == "__main__":
    main()
