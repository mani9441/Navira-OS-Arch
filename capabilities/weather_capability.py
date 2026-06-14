class WeatherCapability:

    async def execute(self, context):
        """
        Executes the weather lookup capability.
        
        Args:
            context (ProcessContext): The runtime context containing 
                                      any active configuration or inputs.
        """
        # You can use context.get_input("city", "Bangalore") here later if needed!
        return {
            "city": "Bangalore",
            "temperature": 29,
            "condition": "Cloudy"
        }