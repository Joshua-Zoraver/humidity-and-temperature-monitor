from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from src.sensor_db import init_db, store_result

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

#Load thresholds from env
load_dotenv()

#Get thresholds from environment, use defaults if not set
TEMP_THRESHOLD = (
    float(os.getenv("TEMP_MIN", 18.0)),
    float(os.getenv("TEMP_MAX", 26.0)),
)
HUMIDITY_THRESHOLD = (
    float(os.getenv("HUMIDITY_MIN", 40.0)),
    float(os.getenv("HUMIDITY_MAX", 70.0)),
)

def evaluate_sensor(value, min_thresh, max_thresh):
    if value is None:
        return "INVALID"
    return "OK" if min_thresh <= value <= max_thresh else "ALERT"

def process_sensor_reading(sensor_data):
    now = datetime.utcnow()
    results = []

    temp_status = evaluate_sensor(sensor_data.get("temperature"), *TEMP_THRESHOLD)
    temp_result = {
        "timestamp": now,
        "sensor": "temperature",
        "value": sensor_data.get("temperature"),
        "status": temp_status
    }

    humidity_status = evaluate_sensor(sensor_data.get("humidity"), *HUMIDITY_THRESHOLD)
    humidity_result = {
        "timestamp": now,
        "sensor": "humidity",
        "value": sensor_data.get("humidity"),
        "status": humidity_status
    }

    for r in [temp_result, humidity_result]:
        logging.info(f"Sensor check: {r}")
        store_result(r)
        results.append(r)

    return results
