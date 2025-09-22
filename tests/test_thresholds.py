import pytest
from datetime import datetime
from src.thresholds import process_sensor_reading

# Helper mock for testing
def mock_store(result):
    mock_store.results.append(result)

mock_store.results = []

def test_sensor_within_thresholds(monkeypatch):
    data = {"temperature": 22.0, "humidity": 50.0}
    mock_store.results = []

    # Patch store_result
    monkeypatch.setattr("src.thresholds.store_result", mock_store)

    results = process_sensor_reading(data)

    for r in results:
        assert r["status"] == "OK"
        assert r["value"] == data[r["sensor"]]

    assert len(mock_store.results) == 2


def test_sensor_outside_thresholds(monkeypatch):
    data = {"temperature": 30.0, "humidity": 35.0}
    mock_store.results = []

    monkeypatch.setattr("src.thresholds.store_result", mock_store)

    results = process_sensor_reading(data)

    status_map = {"temperature": "ALERT", "humidity": "ALERT"}
    for r in results:
        assert r["status"] == status_map[r["sensor"]]
        assert r["value"] == data[r["sensor"]]

    assert len(mock_store.results) == 2


def test_partial_threshold_violation(monkeypatch):
    data = {"temperature": 20.0, "humidity": 75.0}
    mock_store.results = []

    monkeypatch.setattr("src.thresholds.store_result", mock_store)

    results = process_sensor_reading(data)

    expected_status = {"temperature": "OK", "humidity": "ALERT"}
    for r in results:
        assert r["status"] == expected_status[r["sensor"]]

    assert len(mock_store.results) == 2
