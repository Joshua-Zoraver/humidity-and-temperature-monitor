import pytest
import time
from unittest.mock import MagicMock, call
from src import sensors
from src.sensors import SensorReader, read_values

def test_reads_humidity_temperature(monkeypatch):
    '''
    Test that read_values returns correct keys and valid numbers,
    ignoring null or invalid values
    '''
    #Mock SenseHat
    fake_hat = MagicMock()
    fake_hat.get_humidity.return_value = 55.0
    fake_hat.get_temperature.return_value = 22.5
    monkeypatch.setattr(sensors, "sense", fake_hat)

    data = sensors.read_values()

    #Check keys exist
    assert "humidity" in data
    assert "temperature" in data

    #Check values are valid numbers
    assert isinstance(data["humidity"], (int, float))
    assert isinstance(data["temperature"], (int, float))

    #Check values match the mock
    assert data["humidity"] == 55.0
    assert data["temperature"] == 22.5

def test_reads_handles_invalid_values(monkeypatch):
    '''
    Test that invalid sensor values (None, NAN) are handled properly
    '''
    import math

    fake_hat = MagicMock()
    fake_hat.get_humidity.return_value = None
    fake_hat.get_temperature.return_value = float('nan')
    monkeypatch.setattr(sensors, "sense", fake_hat)

    data = sensors.read_values()

    assert data["humidity"] is None
    assert data["temperature"] is None

def test_sensor_reader_thread(monkeypatch):
    import time as real_time

    fake_hat = MagicMock()
    fake_hat.get_humidity.return_value = 60.0
    fake_hat.get_temperature.return_value = 25.0
    monkeypatch.setattr(sensors, "sense", fake_hat)

    callback = MagicMock()
    reader = SensorReader(interval = 0.1, callback = callback)

    #Mock time.sleep for quick testing
    monkeypatch.setattr(time, "sleep", MagicMock())

    #Start thread
    reader.start()

    #Let it run briefly
    time.sleep(0.3)

    #Stop thread
    reader.stop()
    reader.join()

    #Verify callback was called at least once with correct data
    expected_data = {"humidity": 60.0, "temperature": 25.0}
    assert callback.called
    callback.assert_called_with(expected_data)

    #Verify time.sleep was called with correct interval
    time.sleep.assert_called_with(0.1)

def test_sensor_reader_no_callback(monkeypatch):
    fake_hat = MagicMock()
    fake_hat.get_humidity.return_value = 60.0
    fake_hat.get_temperature.return_value = 25.0
    monkeypatch.setattr(sensors, "sense", fake_hat)
    monkeypatch.setattr(time, "sleep", MagicMock())

    reader = SensorReader(interval = 0.1, callback = None)
    reader.start()
    time.sleep(0.1)
    reader.stop()
    reader.join()

def test_sensor_reader_invalid_data(monkeypatch):
    import math
    
    fake_hat = MagicMock()
    fake_hat.get_humidity.return_value = None
    fake_hat.get_temperature.return_value = float('nan')
    monkeypatch.setattr(sensors, "sense", fake_hat)
    callback = MagicMock()
    reader = SensorReader(interval = 0.1, callback = callback)
    monkeypatch.setattr(time, "sleep", MagicMock())

    reader.start()
    time.sleep(0.1)
    reader.stop()
    reader.join()

    callback.assert_called_with({"humidity": None, "temperature": None})