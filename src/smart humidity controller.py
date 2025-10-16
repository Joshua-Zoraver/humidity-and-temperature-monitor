import time
import random
import sqlite3
from gpiozero import OutputDevice

# --- GPIO Setup ---
# Define GPIO pins for actuators
HUMIDIFIER_PIN = 17
DEHUMIDIFIER_PIN = 27

humidifier = OutputDevice(HUMIDIFIER_PIN)
dehumidifier = OutputDevice(DEHUMIDIFIER_PIN)

# --- Humidity Thresholds ---
THRESHOLDS = {
    "VERY_DRY": 45,
    "DRY": 50,
    "OPTIMAL_LOW": 51,
    "OPTIMAL_HIGH": 60,
    "HUMID": 70,
    "VERY_HUMID": 80
}

# --- Database Setup ---
conn = sqlite3.connect('htme_data.db')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    humidity REAL,
    temperature REAL,
    status TEXT,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# --- Simulated Sensor Read Function ---
def read_sensor():
    """Simulate humidity and temperature readings."""
    humidity = random.uniform(35, 90)
    temperature = random.uniform(18, 32)
    return humidity, temperature


# --- Actuator Control Logic ---
def trigger_actuators(humidity):
    """
    Compare humidity with thresholds and trigger actuators accordingly.
    Returns (status, action).
    """
    if humidity < THRESHOLDS["VERY_DRY"]:
        # Very Dry: Turn on humidifier (HIGH)
        humidifier.on()
        dehumidifier.off()
        return "Very Dry", "Humidifier ON (High Mode)"

    elif humidity < THRESHOLDS["DRY"]:
        # Dry: Turn on humidifier (LOW)
        humidifier.on()
        dehumidifier.off()
        return "Dry", "Humidifier ON (Low Mode)"

    elif THRESHOLDS["OPTIMAL_LOW"] <= humidity <= THRESHOLDS["OPTIMAL_HIGH"]:
        # Stable range
        humidifier.off()
        dehumidifier.off()
        return "Optimal", "Stable - No Action"

    elif humidity <= THRESHOLDS["HUMID"]:
        # Humid: turn on dehumidifier (LOW)
        humidifier.off()
        dehumidifier.on()
        return "Humid", "Dehumidifier ON (Low Mode)"

    elif humidity <= THRESHOLDS["VERY_HUMID"]:
        # Very Humid: dehumidifier HIGH
        humidifier.off()
        dehumidifier.on()
        return "Very Humid", "Dehumidifier ON (High Mode)"

    else:
        # Critical level
        humidifier.off()
        dehumidifier.on()
        return "Critical", "ALERT: Critical Humidity Level!"


# --- Main Control Loop ---
print("Smart Humidity Controller Started...")
print("Press Ctrl + C to stop.\n")

try:
    while True:
        # Read sensor data
        humidity, temperature = read_sensor()

        # Apply comparison logic and trigger actuators
        status, action = trigger_actuators(humidity)

        # Display system state
        print(f"Humidity: {humidity:.1f}% | Temp: {temperature:.1f}°C | Status: {status}")
        print(f"Action: {action}")
        print("-" * 60)

        # Log to database
        cur.execute(
            "INSERT INTO sensor_data (humidity, temperature, status, action) VALUES (?, ?, ?, ?)",
            (humidity, temperature, status, action)
        )
        conn.commit()

        time.sleep(10)  # Sample every 10 seconds

except KeyboardInterrupt:
    print("\n Monitoring stopped by user.")

finally:
    # Safely turn off devices and close resources
    humidifier.off()
    dehumidifier.off()
    conn.close()
    print(" GPIO pins and database connection closed.")
