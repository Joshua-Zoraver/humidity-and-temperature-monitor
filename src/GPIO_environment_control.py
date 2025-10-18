from gpiozero import OutputDevice
from src.thresholds import TEMP_THRESHOLD, HUMIDITY_THRESHOLD, evaluate_sensor

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
# Control Logic
# -------------------------------
def control_humidity(hum_value):
    status = evaluate_sensor(hum_value, *HUMIDITY_THRESHOLD)

    if status == "INVALID":
        heater.off()
        fan.off()
        return "INVALID"
    elif status == "LOW":
        humidifier.on()
        dehumidifier.off()
        return "HUMIDIFYING"
    elif status == "HIGH":
        humidifier.off()
        dehumidifier.on()
        return "DEHUMIDIFYING"
    else:
        humidifier.off()
        dehumidifier.off()
        return "STABLE"


def control_temperature(temp_value):
    status = evaluate_sensor(temp_value, *TEMP_THRESHOLD)
    
    if status == "INVALID":
        heater.off()
        fan.off()
        return "INVALID"
    elif status == "LOW":
        heater.on()
        fan.off()
        return "HEATING"
    elif status == "HIGH":
        fan.on()
        heater.off()
        return "COOLING"
    else:
        fan.off()
        heater.off()
        return "STABLE"

def apply_environment_control(sensor_data):
    t_action = control_temperature(sensor_data.get("temperature"))
    h_action = control_humidity(sensor_data.get("humidity"))

    return {
        "temperature_action": t_action,
        "humidity_action": h_action
    }

def shutdown_devices():
    heater.off()
    fan.off()
    humidifier.off()
    dehumidifier.off()
