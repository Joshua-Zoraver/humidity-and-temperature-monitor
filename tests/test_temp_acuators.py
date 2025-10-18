import time

# --- Mock GPIO class for Mac/PC ---
class MockDevice:
    def __init__(self, name):
        self.name = name
        self.state = False

    def on(self):
        self.state = True
        print(f" {self.name} -> ON")

    def off(self):
        self.state = False
        print(f" {self.name} -> OFF")


# --- Replace GPIO pins with mock devices ---
heater = MockDevice("Heater")
fan = MockDevice("Fan")

# --- Temperature Thresholds ---
TEMP_THRESHOLDS = {
    "VERY_COLD": 15,
    "COLD": 20,
    "OPTIMAL_LOW": 21,
    "OPTIMAL_HIGH": 27,
    "WARM": 30,
    "VERY_HOT": 35
}

# --- Control Logic ---
def control_temperature(temperature):
    if temperature < TEMP_THRESHOLDS["VERY_COLD"]:
        heater.on()
        fan.off()
        return " Very Cold", "Heater ON (High)"
    elif temperature < TEMP_THRESHOLDS["COLD"]:
        heater.on()
        fan.off()
        return "Cold", "Heater ON (Low)"
    elif TEMP_THRESHOLDS["OPTIMAL_LOW"] <= temperature <= TEMP_THRESHOLDS["OPTIMAL_HIGH"]:
        heater.off()
        fan.off()
        return " Ideal", "Stable (No Action)"
    elif temperature <= TEMP_THRESHOLDS["WARM"]:
        fan.on()
        heater.off()
        return "Warm", "Fan ON (Low)"
    elif temperature <= TEMP_THRESHOLDS["VERY_HOT"]:
        fan.on()
        heater.off()
        return " Very Hot", "Fan ON (High)"
    else:
        fan.on()
        heater.off()
        return " Critical", "Emergency Fan Mode"


# --- Test Simulation ---
SIMULATED_TEMPS = [12, 18, 22, 26, 29, 33, 37]

for temp in SIMULATED_TEMPS:
    status, action = control_temperature(temp)
    print(f"Temperature: {temp:.1f}°C | Status: {status} | Action: {action}")
    time.sleep(1)

# Turn everything off at the end
heater.off()
fan.off()
