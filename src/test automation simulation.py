import time
import random

# --- Simulated GPIO Device Classes ---
class MockDevice:
    """Mock GPIO device to simulate ON/OFF states."""
    def __init__(self, name):
        self.name = name
        self.state = False

    def on(self):
        self.state = True
        print(f" {self.name} -> ON")

    def off(self):
        self.state = False
        print(f" {self.name} -> OFF")


# --- Mock Actuators (instead of GPIO pins) ---
humidifier = MockDevice("Humidifier")
dehumidifier = MockDevice("Dehumidifier")

# --- Threshold Definitions ---
THRESHOLDS = {
    "VERY_DRY": 45,
    "DRY": 50,
    "OPTIMAL_LOW": 51,
    "OPTIMAL_HIGH": 60,
    "HUMID": 70,
    "VERY_HUMID": 80
}

# --- Comparison + Control Logic ---
def trigger_actuators(humidity):
    """Decide which device to activate based on humidity."""
    if humidity < THRESHOLDS["VERY_DRY"]:
        humidifier.on()
        dehumidifier.off()
        return "Very Dry", "Humidifier ON (High Mode)"
    elif humidity < THRESHOLDS["DRY"]:
        humidifier.on()
        dehumidifier.off()
        return "Dry", "Humidifier ON (Low Mode)"
    elif THRESHOLDS["OPTIMAL_LOW"] <= humidity <= THRESHOLDS["OPTIMAL_HIGH"]:
        humidifier.off()
        dehumidifier.off()
        return "Optimal", "Stable - No Action"
    elif humidity <= THRESHOLDS["HUMID"]:
        humidifier.off()
        dehumidifier.on()
        return "Humid", "Dehumidifier ON (Low Mode)"
    elif humidity <= THRESHOLDS["VERY_HUMID"]:
        humidifier.off()
        dehumidifier.on()
        return "Very Humid", "Dehumidifier ON (High Mode)"
    else:
        humidifier.off()
        dehumidifier.on()
        return "Critical", "ALERT: Critical Humidity Level!"


# --- Simulation Function ---
def simulate_humidity_changes():
    """Simulate humidity readings over time."""
    humidity = random.uniform(35, 85)
    direction = 1  # 1 = rising, -1 = falling

    print("\n Starting Device Automation Simulation\n")
    print("Press Ctrl + C to stop.\n")

    try:
        while True:
            # Small random variation to simulate environmental change
            humidity += random.uniform(-2, 2) * direction

            # Flip direction if limits exceeded (to oscillate humidity)
            if humidity >= 90:
                direction = -1
            elif humidity <= 35:
                direction = 1

            # Apply control logic
            status, action = trigger_actuators(humidity)

            # Display system status
            print(f"Humidity: {humidity:.1f}% | Status: {status} | Action: {action}")
            print("-" * 60)

            time.sleep(2)  # simulate every 2 seconds

    except KeyboardInterrupt:
        print("\n Simulation stopped by user.")
        humidifier.off()
        dehumidifier.off()


# --- Run Simulation ---
if __name__ == "__main__":
    simulate_humidity_changes()
