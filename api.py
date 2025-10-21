from flask import Flask, jsonify, request, send_from_directory
from src.sensor_db import get_recent_data, store_result
from src.sensors import read_values
from src.thresholds import TEMP_THRESHOLD, HUMIDITY_THRESHOLD, evaluate_sensor

app = Flask(__name__)

# -------------------------------
# Live local Pi sensor readings
# -------------------------------
@app.route("/sensor-data", methods=["GET"])
def get_sensor_data():
    data = read_values()  # Only for this Pi
    data["temp_status"] = evaluate_sensor(data.get("temperature"), *TEMP_THRESHOLD)
    data["humidity_status"] = evaluate_sensor(data.get("humidity"), *HUMIDITY_THRESHOLD)
    return jsonify(data), 200

# -------------------------------
# Receive data from other Pis
# -------------------------------
@app.route("/submit-data", methods=["POST"])
def submit_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        store_result({
            "timestamp": data["timestamp"],
            "sensor": data["sensor"],
            "value": data["value"],
            "status": data["status"],
            "pi_id": data.get("pi_id", "unknown")
        })
        return jsonify({"message": "Data stored"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Serve dashboard
# -------------------------------
@app.route("/")
def serve_dashboard():
    return send_from_directory(".", "index.html")

# -------------------------------
# History table
# -------------------------------
@app.route("/history", methods=["GET"])
def get_history():
    try:
        data = get_recent_data(limit=20)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
