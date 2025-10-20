import os
import sqlite3
import tempfile
import pytest
import datetime
import logging
from unittest.mock import MagicMock
from src import sensor_db

@pytest.fixture
def temp_db(monkeypatch):
    #Create a temporary database file and override DB_PATH for testing
    #Cleans up after each test
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.close()
    monkeypatch.setattr(sensor_db, "DB_PATH", tmpfile.name)
    yield tmpfile.name
    os.remove(tmpfile.name)

def test_init_db_makes_table(temp_db):
    #Test that init_db creates the sensor_data table correctly
    sensor_db.init_db()

    con = sqlite3.connect(temp_db)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_data';")
    result = cur.fetchone()
    con.close()

    assert result is not None

def test_store_result_inserts_row(temp_db, monkeypatch):
    #Test that store_result correctly inserts a row into the database
    sensor_db.init_db()
    fake_result = {
        "timestamp": datetime.datetime.now(),
        "sensor": "temperature",
        "value": 23.5,
        "status": "OK"
    }

    mock_log = MagicMock()
    monkeypatch.setattr(logging, "info", mock_log)

    sensor_db.store_result(fake_result)

    con = sqlite3.connect(temp_db)
    cur = con.cursor()
    cur.execute("SELECT sensor, value, status FROM sensor_data;")
    row = cur.fetchone()
    con.close()

    assert row == ("temperature", 23.5, "OK")
    mock_log.assert_called()

def test_store_result_handle_error(monkeypatch, temp_db):
    #Test that store_result logs an error if the db insertion fails
    monkeypatch.setattr(sqlite3, "connect", MagicMock(side_effect=Exception("DB failure")))

    fake_result = {
        "timestamp": datetime.datetime.now(),
        "sensor": "humidity",
        "value": 50.1,
        "status": "FAIL"
    }

    mock_log_error = MagicMock()
    monkeypatch.setattr(logging, "error", mock_log_error)

    sensor_db.store_result(fake_result)

    mock_log_error.assert_called()
    assert "DB failure" in mock_log_error.call_args[0][0]

def test_get_recent_data_returns_correct_rows(temp_db):
     #Test that get_recent_data in the correct format and order
     sensor_db.init_db()

     con = sqlite3.connect(temp_db)
     cur = con.cursor()
     sample_data = [
         ("2025-01-01T00:00:00", "humidity", 45.0, "OK"),
         ("2025-01-02T00:00:00", "temperature", 22.5, "OK"),
         ("2025-01-03T00:00:00", "humidity", 47.0, "OK"),
     ]
     cur.executemany("INSERT INTO sensor_data (timestamp, sensor, value, status) VALUES (?, ?, ?, ?)", sample_data)
     con.commit()
     con.close()

     data = sensor_db.get_recent_data(limit=2)

     assert isinstance(data, list)
     assert len(data) == 2
     assert data[0]["timestamp"] == "2025-01-03T00:00:00"
     assert all(k in data[0] for k in ("timestamp", "sensor", "value", "status"))
