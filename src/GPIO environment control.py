import time
import adafruit_dht
import board
from gpiozero import OutputDevice

# -------------------------------
# GPIO Pin Assignments (BCM Mode)
# -------------------------------
HUMIDIFIER_PIN = 17
DEHUMIDIFIER_PIN = 27
HEATER_PIN = 22
FAN_PIN = 23

# -------------------------------
# Devices (GPIO Controlled)
# -------------------------------
humidifier = OutputDevice(HUMIDIFIER_PIN, active_high=True, initial_value=False)
dehumidifier = OutputDevice(DEHUMIDIFIER_PIN, active_high=True, initial_value=False)
heater = OutputDevice(HEATER_PIN, active_high=True, initial_value=False)
fan = OutputDevice(FAN_PIN, active_high=True, initial_value=False)

# -------------------------------
# Sensor Setup (DHT22)
# -------------------------------
dht_sensor = adafruit_dht.DHT22(board.D4)  # D4 = GPIO 4

# -------------------------------
# Threshold Definitions
# -------------------------------
HUMIDITY_THRESHOLDS = {
    "VERY_DRY": 45,
    "DRY": 50,
    "OPTIMAL_LOW": 51,
    "OPTIMAL_HIGH": 60,
    "HUMID": 70,
    "VERY_HUMID": 80
}

TEMP_THRESHOLDS = {
    "MIN": 20,   # °C - turn on heater if below
    "MAX": 28    # °C - turn on fan if above
}

# -------------------------------
# Control Logic
# -------------------------------
def control_humidity(humidity):
    if humidity < HUMIDITY_THRESHOLDS["VERY_DRY"]:
        humidifier.on()
        dehumidifier.off()
        return "Very Dry", "Humidifier ON (High Mode)"
    elif humidity < HUMIDITY_THRESHOLDS["DRY"]:
        humidifier.on()
        dehumidifier.off()
        return "Dry", "Humidifier ON (Low Mode)"
    elif HUMIDITY_THRESHOLDS["OPTIMAL_LOW"] <= humidity <= HUMIDITY_THRESHOLDS["OPTIMAL_HIGH"]:
        humidifier.off()
        dehumidifier.off()
        return "Optimal", "Stable"
    elif humidity <= HUMIDITY_THRESHOLDS["HUMID"]:
        humidifier.off()
        dehumidifier.on()
        return "Humid", "Dehumidifier ON (Low Mode)"
    elif humidity <= HUMIDITY_THRESHOLDS["VERY_HUMID"]:
        humidifier.off()
        dehumidifier.on()
        return "Very Humid", "Dehumidifier ON (High Mode)"
    else:
        humidifier.off()
        dehumidifier.on()
        return "Critical", " ALERT: Critical Humidity Level"


def control_temperature(temperature):
    if temperature < TEMP_THRESHOLDS["MIN"]:
        heater.on()
        fan.off()
        return "Too Cold", "Heater ON"
    elif temperature > TEMP_THRESHOLDS["MAX"]:
        fan.on()
        heater.off()
        return "Too Hot", "Fan ON"
    else:
        fan.off()
        heater.off()
        return "Ideal", "Temperature Stable"

# -------------------------------
# Main Control Loop
# -------------------------------
def run_environment_control():
    print(" GPIO Smart Environment Controller Running...\nPress Ctrl+C to stop.\n")

    try:
        while True:
            try:
                temperature = dht_sensor.temperature
                humidity = dht_sensor.humidity

                if humidity is None or temperature is None:
                    print(" Sensor read error. Retrying...")
                    time.sleep(2)
                    continue

                # Run control logic
                h_status, h_action = control_humidity(humidity)
                t_status, t_action = control_temperature(temperature)

                print(f"Humidity: {humidity:.1f}% | Temp: {temperature:.1f}°C")
                print(f"→ Humidity: {h_status} | Action: {h_action}")
                print(f"→ Temperature: {t_status} | Action: {t_action}")
                print("-" * 80)

                time.sleep(5)

            except RuntimeError as e:
                # DHT sensors often throw intermittent errors; just retry
                print(f" DHT read error: {e}")
                time.sleep(2)
                continue

    except KeyboardInterrupt:
        print("\n Stopping environment control...")

    finally:
        # Ensure all devices are off
        humidifier.off()
        dehumidifier.off()
        heater.off()
        fan.off()
        print(" All devices turned OFF safely.")


# -------------------------------
# Run Script
# -------------------------------
if __name__ == "__main__":
    run_environment_control()
