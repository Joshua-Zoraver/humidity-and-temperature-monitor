import sqlite3
import logging
from datetime import datetime

DB_PATH = "src/sensor_data.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sensor TEXT NOT NULL,
            value REAL,
            status TEXT NOT NULL,
            pi_id TEXT NOT NULL DEFAULT 'host'
        )
    """)
    con.commit()
    con.close()
    logging.info(f"Database initialized at {DB_PATH}")

def store_result(result, pi_id="host"):
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        cur.execute("""
            INSERT INTO sensor_data (timestamp, sensor, value, status, pi_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            result["timestamp"].isoformat(),
            result["sensor"],
            result["value"],
            result["status"],
            pi_id
        ))

        con.commit()
        con.close()
        logging.info(f"Stored result in DB from {pi_id}: {result}")
    except Exception as e:
        logging.error(f"Failed to store result: {e}")

def store_remote_data(data):
    """Store data received from remote Pis"""
    try:
        pi_id = data.get("pi_id", "unknown")
        timestamp = datetime.now()
        
        #Store temperature
        if "temperature" in data:
            temp_result = {
                "timestamp": timestamp,
                "sensor": "temperature",
                "value": data["temperature"],
                "status": data.get("temp_status", "UNKNOWN")
            }
            store_result(temp_result, pi_id)
        
        #Store humidity
        if "humidity" in data:
            humidity_result = {
                "timestamp": timestamp,
                "sensor": "humidity",
                "value": data["humidity"],
                "status": data.get("humidity_status", "UNKNOWN")
            }
            store_result(humidity_result, pi_id)
            
    except Exception as e:
        logging.error(f"Failed to store remote data: {e}")

def get_recent_data(limit=20, pi_id=None):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
    
    if pi_id:
        #Get data for specific Pi
        cur.execute("""
            SELECT timestamp, sensor, value, status, pi_id
            FROM sensor_data
            WHERE pi_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (pi_id, limit))
    else:
        #Get all recent data
        cur.execute("""
            SELECT timestamp, sensor, value, status, pi_id
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
    rows = cur.fetchall()
    con.close()
    return [dict(row) for row in rows]