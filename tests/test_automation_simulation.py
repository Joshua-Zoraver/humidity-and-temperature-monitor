import pytest
from gpiozero import OutputDevice
from unittest.mock import Mock, patch, MagicMock
from src.GPIO_environment_control import (
    control_humidity,
    control_temperature,
    apply_environment_control,
    shutdown_devices
)
import src.GPIO_environment_control as env_control

@pytest.fixture
def mock_devices(monkeypatch):
    mock_humidifier = Mock()
    mock_dehumidifier = Mock()
    mock_heater = Mock()
    mock_fan = Mock()

    monkeypatch.setattr(env_control, 'humidifier', mock_humidifier)
    monkeypatch.setattr(env_control, 'dehumidifier', mock_dehumidifier)
    monkeypatch.setattr(env_control, 'heater', mock_heater)
    monkeypatch.setattr(env_control, 'fan', mock_fan)

    return {
        'humidifier': mock_humidifier,
        'dehumidifier': mock_dehumidifier,
        'heater': mock_heater,
        'fan': mock_fan
    }

@pytest.fixture
def mock_evaluate_sensor(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(env_control, 'evaluate_sensor', mock)
    return mock

class TestControlHumidity:
    def test_humidity_invalid(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "INVALID"

        result = control_humidity(None)

        assert result == "INVALID"
        mock_devices['heater'].off.assert_called_once()
        mock_devices['fan'].off.assert_called_once()

    def test_humidity_low(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "LOW"

        result = control_humidity(30.0)

        assert result == "HUMIDIFYING"
        mock_devices['humidifier'].on.assert_called_once()
        mock_devices['dehumidifier'].off.assert_called_once()

    def test_humidity_high(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "HIGH"

        result = control_humidity(80.0)

        assert result == "DEHUMIDIFYING"
        mock_devices['humidifier'].off.assert_called_once()
        mock_devices['dehumidifier'].on.assert_called_once()

    def test_humidity_stable(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "STABLE"

        result = control_humidity(50.0)

        assert result == "STABLE"
        mock_devices['humidifier'].off.assert_called_once()
        mock_devices['dehumidifier'].off.assert_called_once()

class TestControlTemperature:
    def test_temperature_invalid(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "INVALID"

        result = control_temperature(None)

        assert result == "INVALID"
        mock_devices['heater'].off.assert_called_once()
        mock_devices['fan'].off.assert_called_once()

    def test_temperature_low(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "LOW"

        result = control_temperature(15.0)

        assert result == "HEATING"
        mock_devices['heater'].on.assert_called_once()
        mock_devices['fan'].off.assert_called_once()

    def test_temperature_high(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "HIGH"

        result = control_temperature(30.0)

        assert result == "COOLING"
        mock_devices['heater'].off.assert_called_once()
        mock_devices['fan'].on.assert_called_once()

    def test_temperature_stable(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.return_value = "STABLE"

        result = control_temperature(22.0)

        assert result == "STABLE"
        mock_devices['fan'].off.assert_called_once()
        mock_devices['heater'].off.assert_called_once()

class TestApplyEnvironmentControl:
    def test_apply_both_control(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.side_effect = ["LOW", "HIGH"]

        sensor_data = {
            "temperature": 15.0,
            "humidity": 80.0
        }

        result = apply_environment_control(sensor_data)

        assert result == {
            "temperature_action": "HEATING",
            "humidity_action": "DEHUMIDIFYING"
        }

    def test_apply_stable_conditions(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.side_effect = ["STABLE", "STABLE"]

        sensor_data = {
            "temperature": 22.0,
            "humidity": 50.0
        }

        result = apply_environment_control(sensor_data)

        assert result == {
            "temperature_action": "STABLE",
            "humidity_action": "STABLE"
        }

    def test_apply_invalid_sensors(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.side_effect = ["INVALID", "INVALID"]

        sensor_data = {
            "temperature": None,
            "humidity": None
        }

        result = apply_environment_control(sensor_data)

        assert result == {
            "temperature_action": "INVALID",
            "humidity_action": "INVALID"
        }

    def test_apply_missing_sensor_keys(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.side_effect = ["INVALID", "INVALID"]

        sensor_data = {}

        result = apply_environment_control(sensor_data)

        assert result == {
            "temperature_action": "INVALID",
            "humidity_action": "INVALID"
        }

class TestShutdown:
    def test_shutdown_devices(self, mock_devices):
        shutdown_devices()

        mock_devices['heater'].off.assert_called_once()
        mock_devices['fan'].off.assert_called_once()
        mock_devices['humidifier'].off.assert_called_once()
        mock_devices['dehumidifier'].off.assert_called_once()


class TestIntegration:
    def test_heating_humidifying(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.side_effect = ["LOW", "LOW"]

        sensor_data = {"temperature": 15.0, "humidity": 30.0}
        result = apply_environment_control(sensor_data)

        assert result["temperature_action"] == "HEATING"
        assert result["humidity_action"] == "HUMIDIFYING"
        mock_devices['heater'].on.assert_called()
        mock_devices['humidifier'].on.assert_called()

    def test_cooling_dehumidifying(self, mock_devices, mock_evaluate_sensor):
        mock_evaluate_sensor.side_effect = ["HIGH", "HIGH"]

        sensor_data = {"temperature": 30.0, "humidity": 80.0}
        result = apply_environment_control(sensor_data)

        assert result["temperature_action"] == "COOLING"
        assert result["humidity_action"] == "DEHUMIDIFYING"
        mock_devices['fan'].on.assert_called()
        mock_devices['dehumidifier'].on.assert_called()
