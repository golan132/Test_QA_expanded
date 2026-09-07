from src.testing.ammeter_client import AmmeterClient

class AmmeterFactory:
    # Default commands according to specs
    _COMMANDS = {
        "greenlee": b'MEASURE_GREENLEE -get_measurement',
        "entes": b'MEASURE_ENTES -get_data',
        "circutor": b'MEASURE_CIRCUTOR -get_measurement'
    }
    
    # Default ports
    _PORTS = {
        "greenlee": 5000,
        "entes": 5001,
        "circutor": 5002
    }

    @classmethod
    def get_client(cls, ammeter_type: str, timeout: float = 2.0) -> AmmeterClient:
        ammeter_type = ammeter_type.lower()
        if ammeter_type not in cls._COMMANDS:
            raise ValueError(f"Unknown ammeter type: {ammeter_type}")
            
        return AmmeterClient(
            port=cls._PORTS[ammeter_type],
            command=cls._COMMANDS[ammeter_type],
            timeout=timeout
        )
