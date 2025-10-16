import time
import random
from gpiozero import OutputDevice

# =========================================================
#  GPIO Pin Configuration (BCM mode)
# =========================================================
HUMIDIFIER_PIN = 17
DEHUMIDIFIER_PIN = 27
HEATER_PIN = 22
FAN_PIN = 23

humidifier = OutputDevice(HUMIDIFIER_PIN, active_high=True, initial_value=False)
dehumidifier = OutputDevice(DEHUMIDIFIER_PIN, active_high=True, initial_value=False)
heater = OutputDevice(HEATER_PIN, active_high=True, initial_value=False)
fan = OutputDevice(FAN_PIN, active_high=True, initial_value=False)

# =========================================================
#  Humidity Thresholds (%)
# =========================================================
HUMIDITY_THRESHOLDS = {
    "VERY_DRY": 45,
    "DRY": 50,
    "OPTIMAL_LOW": 51,
    "OPTIMAL_HIGH": 65,
    "HUMID": 75,
    "VERY_HUMID": 85
}

# =========================================================
#  Temperature Thresholds (°C)
# =========================================================
TEMP_THRESHOLDS = {
    "VERY_COLD": 15,   # Heater high
    "COLD": 20,        # Heater low
    "OPTIMAL_LOW": 21,
    "OPTIMAL_HIGH": 27,
    "WARM": 30,        # Fan low
    "VERY_HOT": 35     # Fan high
}

# =========================================================
#  Simulated Sensor Readings (Replace with DHT sensor later)
# =========================================================
def read_sensor():
    """Simulate humidity and temperature values."""
    humidity = random.uniform(35, 90)
    temperature = random.uniform(12, 38)
    return humidity, temperature

# =========================================================
#  Humidity Control Logic → Actuator Trigger
# =========================================================
def control_humidity(humidity):
    if humidity < HUMIDITY_THRESHOLDS["VERY_DRY"]:
        humidifier.on()
        dehumidifier.off()
        return " Very Dry", "Humidifier ON (High)"
    elif humidity < HUMIDITY_THRESHOLDS["DRY"]:
        humidifier.on()
        dehumidifier.off()
        return "Dry", "Humidifier ON (Low)"
    elif HUMIDITY_THRESHOLDS["OPTIMAL_LOW"] <= humidity <= HUMIDITY_THRESHOLDS["OPTIMAL_HIGH"]:
        humidifier.off()
        dehumidifier.off()
        return " Optimal", "Stable"
    elif humidity <= HUMIDITY_THRESHOLDS["HUMID"]:
        humidifier.off()
        dehumidifier.on()
        return "Humid", "Dehumidifier ON (Low)"
    elif humidity <= HUMIDITY_THRESHOLDS["VERY_HUMID"]:
        humidifier.off()
        dehumidifier.on()
        return " Very Humid", "Dehumidifier ON (High)"
    else:
        humidifier.off()
        dehumidifier.on()
        return " Critical", "Emergency Dehumidifier Mode"

# =========================================================
#  Temperature Control Logic → Actuator Trigger
# ======================

