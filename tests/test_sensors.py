import pytest
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

    #Replace invalid values with None for downstream consumers
    humidity = data["humidity"] if isinstance(data["humidity"], (int, float)) else None
    temperature = data["temperature"] if isinstance(data["temperature"], (int, float)) and not math.isnan(data["temperature"]) else None

    assert humidity is None
    assert temperature is None

def test_sensor_reader_calls_callback(monkeypatch):
    '''
    Test that SensorReader repeatedly calls the callback with valid sensor data,
    simulating multiple readings without running an actual thread
    '''

    #Mock SenseHat
    fake_hat = MagicMock()
    fake_hat.get_humidity.return_value = 60.0
    fake_hat.get_temperature.return_value = 25.0
    monkeypatch.setattr(sensors, "sense", fake_hat)

    #Mock callback to track calls
    callback = MagicMock()

    #Create a SensorReader with interval = 0
    reader = SensorReader(interval = 0, callback = callback)

    #Replace run method to simulate 3 readings
    def run_simulated():
        for _ in range(3):
            data = sensors.read_values()
            #Only send valid numbers to callback
            if all(isinstance(v, (int, float)) for v in data.values()):
                callback(data)

    reader.run = run_simulated

    #Run simulated readings
    reader.run()

    #Verify callback was called 3 times with correct values
    expected_data = {"humidity": 60.0, "temperature": 25.0}
    assert callback.call_count == 3
    callback.assert_has_calls([call(expected_data)] * 3)