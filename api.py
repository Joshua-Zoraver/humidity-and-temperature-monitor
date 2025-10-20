from flask import Flask, jsonify, send_from_directory
from src.sensors import read_values
from src.thresholds import TEMP_THRESHOLD, HUMIDITY_THRESHOLD, evaluate_sensor
from src.sensor_db import get_recent_data

app = Flask(__name__)

@app.route("/sensor-data", methods=["GET"])
def get_sensor_data():
    data = read_values()
    data["temp_status"] = evaluate_sensor(data.get("temperature"), *TEMP_THRESHOLD)
    data["humidity_status"] = evaluate_sensor(data.get("humidity"), *HUMIDITY_THRESHOLD)
    return jsonify(data), 200

@app.route("/")
def serve_dashboard():
    return send_from_directory(".", "index.html")

@app.route("/history", methods=["GET"])
def get_history():
    try:
        data = get_recent_data(limit=20)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
