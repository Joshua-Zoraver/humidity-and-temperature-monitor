import sqlite3
import logging

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
            status TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()
    logging.info(f"Database initialized at {DB_PATH}")

def store_result(result):
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()

        cur.execute("""
            INSERT INTO sensor_data (timestamp, sensor, value, status)
            VALUES (?, ?, ?, ?)
        """, (
            result["timestamp"].isoformat(),
            result["sensor"],
            result["value"],
            result["status"]
        ))

        con.commit()
        con.close()
        logging.info(f"Stored result in DB: {result}")
    except Exception as e:
        logging.error(f"Failed to store result: {e}")

def get_recent_data(limit=20):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row 
    cur = con.cursor()
    cur.execute("""
        SELECT timestamp, sensor, value, status
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    con.close()
    return [dict(row) for row in rows]
