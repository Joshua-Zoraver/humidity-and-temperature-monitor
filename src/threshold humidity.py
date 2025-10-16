import time
import random
import sqlite3

# --- Sensor Reading (Simulated) ---
def read_sensor():
    """Simulate humidity and temperature readings."""
    humidity = random.uniform(35, 90)      # Simulated humidity (%)
    temperature = random.uniform(18, 32)   # Simulated temperature (°C)
    return humidity, temperature


# --- Humidity Threshold Levels ---
# (values in percentage)
THRESHOLDS = {
    "VERY_DRY": 45,
    "DRY": 50,
    "OPTIMAL": 60,
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

print("️Humidity & Temperature Monitoring Started...")
print("Press Ctrl + C to stop.\n")

# --- Main Loop ---
try:
    while True:
        humidity, temperature = read_sensor()

        # --- Threshold Comparison ---
        if humidity < THRESHOLDS["VERY_DRY"]:
            status = "Very Dry"
            action = "Activate Humidifier (High Mode)"
        elif humidity < THRESHOLDS["DRY"]:
            status = "Dry"
            action = "Activate Humidifier (Low Mode)"
        elif humidity <= THRESHOLDS["OPTIMAL"]:
            status = "Optimal"
            action = "Stable — No Action Needed"
        elif humidity <= THRESHOLDS["HUMID"]:
            status = "Humid"
            action = "Activate Dehumidifier (Low Mode)"
        elif humidity <= THRESHOLDS["VERY_HUMID"]:
            status = "Very Humid"
            action = "Activate Dehumidifier (High Mode)"
        else:
            status = "Critical"
            action = "ALERT: Critical Humidity Level!"

        # --- Display Output ---
        print(f"Humidity: {humidity:.1f}% | Temp: {temperature:.1f}°C | Status: {status}")
        print(f"Action: {action}")
        print("-" * 60)

        # --- Log to Database ---
        cur.execute(
            "INSERT INTO sensor_data (humidity, temperature, status, action) VALUES (?, ?, ?, ?)",
            (humidity, temperature, status, action)
        )
        conn.commit()

        time.sleep(10)  # Delay between readings

except KeyboardInterrupt:
    print("\n Monitoring stopped by user.")

finally:
    conn.close()
    print(" Database connection closed.")
