import time
import requests
import json
from src.sensors import SensorReader, read_values
from src.thresholds import TEMP_THRESHOLD, HUMIDITY_THRESHOLD, evaluate_sensor

class DataSender:
    def __init__(self, host_url, pi_id, interval=10):
        self.host_url = host_url
        self.pi_id = pi_id
        self.interval = interval
        
    def send_data(self, sensor_data):
        """Send sensor data to host Pi"""
        try:
            # Add evaluation and Pi ID to data
            sensor_data["temp_status"] = evaluate_sensor(
                sensor_data.get("temperature"), *TEMP_THRESHOLD
            )
            sensor_data["humidity_status"] = evaluate_sensor(
                sensor_data.get("humidity"), *HUMIDITY_THRESHOLD
            )
            sensor_data["pi_id"] = self.pi_id
            
            # Send to host
            response = requests.post(
                f"{self.host_url}/remote-data",
                json=sensor_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"[{self.pi_id}] Data sent successfully")
            else:
                print(f"[{self.pi_id}] Failed to send data: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[{self.pi_id}] Network error: {e}")
        except Exception as e:
            print(f"[{self.pi_id}] Error sending data: {e}")

def main():
    # Configuration - update these for each client Pi
    HOST_URL = "http://192.168.1.100:5000"  # Host Pi's IP address
    PI_ID = "pi_client_1"  # Unique ID for this Pi
    
    print(f"[{PI_ID}] Starting client data sender")
    print(f"[{PI_ID}] Connecting to host: {HOST_URL}")
    
    sender = DataSender(HOST_URL, PI_ID)
    
    # Create sensor reader that sends data to host
    reader = SensorReader(interval=10, callback=sender.send_data)
    reader.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n[{PI_ID}] Stopping...")
        reader.stop()
        reader.join()
        print(f"[{PI_ID}] Shutdown complete.")

if __name__ == "__main__":
    main()