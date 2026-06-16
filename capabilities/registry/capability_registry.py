# capabilities/registry/capability_registry.py
from typing import Dict, List, Optional, Any

class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, Any] = {}

    # capabilities/registry/capability_registry.py

    def register(self, capability) -> None:
        if not hasattr(capability, "name") or not capability.name:
            raise ValueError("Capability must define a valid string attribute 'name'.")
        
        # 1. Register under its explicit configuration property name (e.g., 'get_weather_forecast')
        self._capabilities[capability.name] = capability
        
        # 2. OLD ARCHITECTURE COMPATIBILITY FALLBACK
        # Also register under the class name string (e.g., 'WeatherCapability')
        class_name = capability.__class__.__name__
        self._capabilities[class_name] = capability
        
        print(f"[REGISTRY] Registered core capability: '{capability.name}' (Class: {class_name})")

    def get(self, name: str):
        """Fetches the instance matching either property name or class name string."""
        return self._capabilities.get(name)

    def list_names(self) -> List[str]:
        # --- FIXED TYPO HERE ---
        return list(self._capabilities.keys())
    
    def list_all(self) -> List[Any]:
        # --- FIXED TYPO HERE ---
        return list(self._capabilities.values())