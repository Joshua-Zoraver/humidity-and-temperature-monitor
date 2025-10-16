import time
import random
from gpiozero import OutputDevice

# -------------------------------
# GPIO Pin Setup (BCM numbering)
# -------------------------------
HEATER_PIN = 22
FAN_PIN = 23

heater = OutputDevice(HEATER_PIN, active_high=True, initial_value=False)
fan = OutputDevice(FAN_PIN, active_high=True, initial_value=False)

# -------------------------------
# Temperature Thresholds (°C)
# -------------------------------
TEMP_THRESHOLDS = {
    "VERY_COLD": 15,   # Heater HIGH
    "COLD": 20,        # Heater LOW
    "OPTIMAL_LOW": 21,
    "OPTIMAL_HIGH": 27,
    "WARM": 30,        # Fan LOW
    "VERY_HOT": 35     # Fan HIGH
}

# -------------------------------
# Simulated Temperature Reading
# (Replace with DHT or real sensor later)
# -------------------------------
def read_temperature():
    return random.uniform(10, 38)  # Simulated temperature in °C

# -------------------------------
# Control Logic for Temperature
# -------------------------------
def control_temperature(temperature):
    if temperature < TEMP_THRESHOLDS["VERY_COLD"]:
        heater.on()
        fan.off()
        action = "Heater ON (High Mode)"
        level = " Very Cold"
    elif temperature < TEMP_THRESHOLDS["COLD"]:
        heater.on()
        fan.off()
        action = "Heater ON (Low Mode)"
        level = "Cold"
    elif TEMP_THRESHOLDS["OPTIMAL_LOW"] <= temperature <= TEMP_THRESHOLDS["OPTIMAL_HIGH"]:
        heater.off()
        fan.off()
        action = "Stable"
        level = " Optimal"
    elif temperature <= TEMP_THRESHOLDS["WARM"]:
        fan.on()
        heater.off()
        action = "Fan ON (Low Mode)"
        level = "Warm"
    elif temperature <= TEMP_THRESHOLDS["VERY_HOT"]:
        fan.on()
        heater.off()
        action = "Fan ON (High Mode)"
        level = " Very Hot"
    else:
        fan.on()
        heater.off()
        action = " ALERT: Critical Temperature Level"
        level = "Critical"

    return level, action

# -------------
