import pytest
import os
import yaml
from src.utils.config import load_config
from src.testing.constants import MODE_COUNT, MODE_DURATION

@pytest.fixture
def temp_config_file(tmp_path):
    def _create_config(sampling_data):
        file_path = tmp_path / "config.yaml"
        data = {"testing": {"sampling": sampling_data}}
        with open(file_path, "w") as f:
            yaml.dump(data, f)
        return str(file_path)
    return _create_config

def test_load_config_count_mode(temp_config_file):
    path = temp_config_file({"sampling_frequency_hz": 10, "measurements_count": 50, "total_duration_seconds": "NULL"})
    config = load_config(path)
    assert config.mode == MODE_COUNT
    assert config.measurements_count == 50
    assert config.duration_seconds is None

def test_load_config_duration_mode(temp_config_file):
    path = temp_config_file({"sampling_frequency_hz": 2, "measurements_count": "NULL", "total_duration_seconds": 30.5})
    config = load_config(path)
    assert config.mode == MODE_DURATION
    assert config.duration_seconds == 30.5
    assert config.measurements_count is None

def test_strict_validation_both_defined(temp_config_file):
    path = temp_config_file({"sampling_frequency_hz": 5, "measurements_count": 10, "total_duration_seconds": 10})
    with pytest.raises(ValueError, match="Cannot define both"):
        load_config(path)

def test_strict_validation_neither_defined(temp_config_file):
    path = temp_config_file({"sampling_frequency_hz": 5, "measurements_count": "NULL", "total_duration_seconds": "NULL"})
    config = load_config(path)
    assert config.mode == MODE_COUNT
    assert config.measurements_count == 100
    assert config.duration_seconds is None

def test_invalid_frequency(temp_config_file):
    path = temp_config_file({"sampling_frequency_hz": -1, "measurements_count": 10, "total_duration_seconds": "NULL"})
    with pytest.raises(ValueError, match="must be > 0"):
        load_config(path)

def test_config_fallback_on_missing_file():
    config = load_config("this_file_does_not_exist.yaml")
    assert config.mode == MODE_COUNT
    assert config.measurements_count == 100

def test_config_fallback_on_malformed_yaml(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("this is not: valid: yaml: -")
    config = load_config(str(path))
    assert config.mode == MODE_COUNT
    assert config.measurements_count == 100
