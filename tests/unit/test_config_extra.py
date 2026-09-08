import os
import yaml
import pytest
import tempfile
from src.utils.config import load_config
from src.testing.constants import DEFAULT_MEASUREMENTS_COUNT


def test_config_not_found():
    # Covers FileNotFoundError (line 25)
    config = load_config("nonexistent_config.yaml")
    assert config.measurements_count == DEFAULT_MEASUREMENTS_COUNT


def test_config_invalid_yaml():
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(":")
        f_name = f.name

    try:
        config = load_config(f_name)
        assert config.measurements_count == DEFAULT_MEASUREMENTS_COUNT
    finally:
        os.remove(f_name)


def test_config_duration_not_null():
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        yaml.dump({"testing": {"sampling": {"total_duration_seconds": 10}}}, f)
        f_name = f.name

    try:
        config = load_config(f_name)
        assert config.duration_seconds == 10.0
    finally:
        os.remove(f_name)


def test_config_both_count_and_duration():
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        yaml.dump(
            {
                "testing": {
                    "sampling": {"measurements_count": 5, "total_duration_seconds": 10}
                }
            },
            f,
        )
        f_name = f.name

    try:
        with pytest.raises(ValueError, match="Cannot define both"):
            load_config(f_name)
    finally:
        os.remove(f_name)


def test_config_null_fallbacks():
    # Covers timeout_seconds == "NULL" (72), error_rate == "NULL" (76)
    # analysis is None (84), visualization is None (93)
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        yaml.dump(
            {
                "testing": {
                    "sampling": {
                        "timeout_seconds": "NULL",
                        "acceptable_error_rate": "NULL",
                    }
                },
                "analysis": None,
            },
            f,
        )
        f_name = f.name

    try:
        config = load_config(f_name)
        assert config.timeout_seconds == 2.0  # Default
        assert config.acceptable_error_rate == 0.1  # Default
        assert len(config.metrics) > 0
    finally:
        os.remove(f_name)
