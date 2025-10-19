from flask import Flask, jsonify, send_from_directory
from src.sensors import read_values

app = Flask(__name__)

latest_data = {"temperature": None, "humidity": None}

@app.route("/sensor-data", methods=["GET"])
def get_sensor_data():
    return jsonify(read_values()), 200

@app.route("/")
def serve_dashboard():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
