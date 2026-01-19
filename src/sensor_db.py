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
    """Store data received from remote Pis (supports two payload formats)."""
    try:
        pi_id = data.get("pi_id", "unknown")

        # Case A: client sent a processed result row:
        # {timestamp, sensor, value, status, pi_id}
        if "sensor" in data and "value" in data:
            ts = data.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts)
                except ValueError:
                    ts = datetime.now()
            elif ts is None:
                ts = datetime.now()

            result = {
                "timestamp": ts,
                "sensor": data["sensor"],
                "value": data["value"],
                "status": data.get("status", "UNKNOWN"),
            }
            store_result(result, pi_id)
            return  # done

        # Case B: client sent combined raw readings:
        timestamp = datetime.now()

        if "temperature" in data:
            temp_result = {
                "timestamp": timestamp,
                "sensor": "temperature",
                "value": data["temperature"],
                "status": data.get("temp_status", "UNKNOWN"),
            }
            store_result(temp_result, pi_id)

        if "humidity" in data:
            humidity_result = {
                "timestamp": timestamp,
                "sensor": "humidity",
                "value": data["humidity"],
                "status": data.get("humidity_status", "UNKNOWN"),
            }
            store_result(humidity_result, pi_id)

    except Exception as e:
        logging.error(f"Failed to store remote data: {e}")

def get_recent_data(limit=10000, pi_id=None):
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


#Get latest DB write for the cards
def get_latest_per_pi():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("""
        SELECT s1.timestamp, s1.sensor, s1.value, s1.status, s1.pi_id
        FROM sensor_data s1
        JOIN (
            SELECT pi_id, sensor, MAX(timestamp) AS max_ts
            FROM sensor_data
            GROUP BY pi_id, sensor
        ) s2
        ON s1.pi_id = s2.pi_id
        AND s1.sensor = s2.sensor
        AND s1.timestamp = s2.max_ts
        ORDER BY s1.pi_id, s1.sensor
    """)

    rows = cur.fetchall()
    con.close()

    latest = {}

    for r in rows:
        pi = r["pi_id"]

        if pi not in latest:
            latest[pi] = {"pi_id": pi}

        if r["sensor"] == "temperature":
            latest[pi]["temperature"] = r["value"]
            latest[pi]["temp_status"] = r["status"]
            latest[pi]["temp_timestamp"] = r["timestamp"]

        elif r["sensor"] == "humidity":
            latest[pi]["humidity"] = r["value"]
            latest[pi]["humidity_status"] = r["status"]
            latest[pi]["humidity_timestamp"] = r["timestamp"]

    return list(latest.values())

	
