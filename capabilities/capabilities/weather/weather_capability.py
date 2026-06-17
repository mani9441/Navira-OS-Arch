# capabilities/weather_capability.py
from typing import Dict, Any

from capabilities.capability import Capability

class WeatherCapability(Capability):
    def __init__(self):
        self.name = "weather_suite"
        self.description = "Provides real-time atmospheric metrics, multi-day predictive forecast projections, and environmental air quality data maps."
        
        # Central parameter pool for Stage-1 LLM argument extraction
        self.input_schema = {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The target city and state/country name."},
                "days": {"type": "integer", "description": "Number of outlook forecast days requested."}
            }
        }
        
        # Declarative tool sub-routing manifest for Stage-2 Microkernel routing
        self.internal_tools = {
            "get_live_conditions": {
                "description": "Retrieve immediate current atmospheric metrics, ambient temperature, humidity, and visibility maps for a city.",
                "required_fields": ["location"]
            },
            "get_predictive_forecast": {
                "description": "Calculate predictive outlooks, multi-day trends, or explicit forward forecast timelines over a series of days.",
                "required_fields": ["location", "days"]
            },
            "get_air_quality": {
                "description": "Fetch live environmental pollution tracking indexes and particulate matter concentrations (PM2.5/PM10).",
                "required_fields": ["location"]
            }
        }

    async def execute(self, context: Any, sub_tool: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs.get("location")
        
        if sub_tool == "get_live_conditions":
            return {
                "status": "success",
                "data": {"location": location, "temperature": "28°C", "condition": "Clear skies", "humidity": "60%"}
            }
            
        elif sub_tool == "get_predictive_forecast":
            days = inputs.get("days", 1)
            return {
                "status": "success",
                "data": {"location": location, "days_projected": days, "summary": f"Clear skies, 28°C for the next {days} days."}
            }
            
        elif sub_tool == "get_air_quality":
            return {
                "status": "success",
                "data": {"location": location, "aqi": 45, "classification": "Good"}
            }
            
        return {"status": "error", "message": f"Unknown sub-tool path: '{sub_tool}'"}