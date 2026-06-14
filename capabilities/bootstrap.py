import asyncio
from uuid import uuid4

from capability_runtime import (
    CapabilityRuntime
)

from capability_registry import (
    CapabilityRegistry
)

from capability_models import (
    CapabilityRequest
)

from weather_capability import (
    WeatherCapability
)


async def main():

    registry = CapabilityRegistry()

    registry.register(
        WeatherCapability()
    )

    runtime = CapabilityRuntime(
        registry
    )

    request = CapabilityRequest(
        request_id=str(uuid4()),
        capability_name="weather",
        inputs={
            "latitude": 17.55,
            "longitude": 78.57,
            "units": "metric"
        }
    )

    result = await runtime.execute(
        request
    )

    print(result)


asyncio.run(main())