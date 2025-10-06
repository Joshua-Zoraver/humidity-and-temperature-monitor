import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = "sensor_data.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sensor TEXT NOT NULL,
            value REAL NOT NULL,
            status TEXT
        )
    """)
    con.commit()
    con.close()
    logging.info("Database initialized.")

def store_result(result):
    """
    Store a single sensor reading result in the database.
    Expected result format:
    {
        "timestamp": datetime,
        "sensor": "temperature" or "humidity",
        "value": float,
        "status": "OK" or "ALERT"
    }
    """
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            INSERT INTO sensor_data (timestamp, sensor, value, status)
            VALUES (?, ?, ?, ?)
        """, (result["timestamp"], result["sensor"], result["value"], result["status"]))
        con.commit()
        logging.info(f"Stored result in database: {result}")
    except Exception as e:
        logging.error(f"Database insert failed: {e}")
    finally:
        con.close()
