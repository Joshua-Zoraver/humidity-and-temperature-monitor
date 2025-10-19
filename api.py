from flask import Flask, jsonify, send_from_directory
from src.sensors import read_values
from src.thresholds import TEMP_THRESHOLD, HUMIDITY_THRESHOLD, evaluate_sensor

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
