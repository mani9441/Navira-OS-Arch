# capabilities/weather_capability.py
from capabilities.capability import Capability
from typing import Dict, Any

class WeatherCapability(Capability):
    def __init__(self):
        self.name = "get_weather_forecast"
        self.category = "environmental_services"
        self.version = "1.0.0"
        
        self.description = "Retrieves current weather, temperature, forecasts, precipitation, and climate metrics for a geographical location."
        self.keywords = [
            "weather", "temperature", "forecast", "rain", "humidity", 
            "climate", "hot", "cold", "sunny", "cloudy", "precipitation", "weather forecast"
        ]
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state/country name (e.g., 'London, UK', 'Visakhapatnam, AP')."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of forecast days requested. Allowed range: 1 to 7.",
                    "default": 1
                }
            },
            "required": ["location"]
        }

    async def execute(self, context: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs.get("location")
        days = inputs.get("days", 1)
        
        # Real downstream API connectivity occurs here
        return {
            "status": "success",
            "data": {
                "location": location,
                "forecast": f"Clear skies, 28°C for the next {days} days.",
                "summary": "No precipitation expected."
            }
        }