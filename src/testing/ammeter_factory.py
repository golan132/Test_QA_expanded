from src.testing.ammeter_client import AmmeterClient
from src.testing.types import Configuration

class AmmeterFactory:
    @classmethod
    def get_client(cls, ammeter_type: str, config: Configuration) -> AmmeterClient:
        ammeter_type = ammeter_type.lower()
        
        if ammeter_type not in config.ammeters_config:
            raise ValueError(f"Unknown or unconfigured ammeter type: {ammeter_type}")
            
        ammeter_settings = config.ammeters_config[ammeter_type]
        
        port = ammeter_settings.get("port")
        command_str = ammeter_settings.get("command")
        
        if not port or not command_str:
            raise ValueError(f"Missing port or command in config for ammeter type: {ammeter_type}")
            
        return AmmeterClient(
            port=int(port),
            command=command_str.encode('utf-8'),
            timeout=config.timeout_seconds
        )
