from collections import defaultdict

import asyncio


class EventBus:

    def __init__(self):

        self.handlers = (
            defaultdict(list)
        )

    def subscribe(
        self,
        event_name,
        handler
    ):

        self.handlers[
            event_name
        ].append(
            handler
        )

    def unsubscribe(
        self,
        event_name,
        handler
    ):

        if (
            handler
            in
            self.handlers[
                event_name
            ]
        ):

            self.handlers[
                event_name
            ].remove(
                handler
            )

    async def publish(
        self,
        event_name,
        event
    ):

        handlers = (
            self.handlers.get(
                event_name,
                []
            )
        )

        for handler in handlers:

            if asyncio.iscoroutinefunction(
                handler
            ):

                await handler(
                    event
                )

            else:

                handler(
                    event
                )

    def list_events(self):

        return list(
            self.handlers.keys()
        )