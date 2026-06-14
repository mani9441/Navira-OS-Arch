from messaging.events import (
    Event
)


class EventManager:

    def __init__(
        self,
        event_bus
    ):

        self.event_bus = (
            event_bus
        )

    async def publish(
        self,
        event_type,
        source,
        payload
    ):

        event = Event(
            event_type=
                event_type,

            source=
                source,

            payload=
                payload
        )

        await self.event_bus.publish(
            event_type,
            event
        )

        return event

    def subscribe(
        self,
        event_type,
        handler
    ):

        self.event_bus.subscribe(
            event_type,
            handler
        )

    def unsubscribe(
        self,
        event_type,
        handler
    ):

        self.event_bus.unsubscribe(
            event_type,
            handler
        )