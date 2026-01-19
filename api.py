from flask import Flask, jsonify, send_from_directory, request
from src.thresholds import TEMP_THRESHOLD, HUMIDITY_THRESHOLD, evaluate_sensor
from src.sensor_db import get_recent_data, store_remote_data, get_latest_per_pi

app = Flask(__name__)

@app.route("/live", methods=["GET"])
def get_live():
	try:
		return jsonify(get_latest_per_pi()), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

@app.route("/remote-data", methods=["POST"])
def receive_remote_data():
    """Endpoint for client Pis to send their sensor data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        #Store the remote data in database
        store_remote_data(data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def serve_dashboard():
    return send_from_directory(".", "index.html")

@app.route("/history", methods=["GET"])
def get_history():
    try:
        #Modified to include pi_id in query
        data = get_recent_data(limit=10000)  #Increased limit for multiple Pis
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
