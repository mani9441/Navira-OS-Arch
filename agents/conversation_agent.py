class ConversationAgent:

    def __init__(
        self,
        orchestrator,
        event_manager,
        human_manager,
        memory_manager
    ):

        self.orchestrator = (
            orchestrator
        )

        self.event_manager = (
            event_manager
        )

        self.human_manager = (
            human_manager
        )

        self.memory_manager = (
            memory_manager
        )

        self.notifications = []

        self.event_manager.subscribe(
            "process.completed",
            self.on_process_completed
        )

        self.event_manager.subscribe(
            "process.failed",
            self.on_process_failed
        )

        self.event_manager.subscribe(
            "human.requested",
            self.on_human_requested
        )

    async def handle_message(
        self,
        query,
        user_id="user_1",
        conversation_id="conv_1"
    ):

        self.memory_manager.store_conversation(
            conversation_id=
                conversation_id,

            role=
                "user",

            content=
                query
        )

        result = await (
            self.orchestrator.handle_request(
                query=
                    query,

                user_id=
                    user_id,

                conversation_id=
                    conversation_id
            )
        )

        self.memory_manager.store_conversation(
            conversation_id=
                conversation_id,

            role=
                "assistant",

            content=
                (
                    f"Started process "
                    f"{result.process_id}"
                )
        )

        return result

    async def on_process_completed(
        self,
        event
    ):

        result = (
            event.payload.get(
                "result"
            )
        )

        self.memory_manager.store_process(
            process_id=
                event.source,

            data={
                "status":
                    "completed",

                "result":
                    result
            }
        )

        self.notifications.append(
            {
                "type":
                    "process.completed",

                "process_id":
                    event.source,

                "result":
                    result
            }
        )

        print()
        print(
            "[PROCESS COMPLETED]"
        )

        print(
            f"Process: {event.source}"
        )

        print(
            f"Result: {result}"
        )

        print()

    async def on_process_failed(
        self,
        event
    ):

        error = (
            event.payload.get(
                "error"
            )
        )

        self.memory_manager.store_process(
            process_id=
                event.source,

            data={
                "status":
                    "failed",

                "error":
                    error
            }
        )

        self.notifications.append(
            {
                "type":
                    "process.failed",

                "process_id":
                    event.source,

                "error":
                    error
            }
        )

        print()
        print(
            "[PROCESS FAILED]"
        )

        print(error)

        print()

    async def on_human_requested(
        self,
        event
    ):

        question = (
            event.payload[
                "question"
            ]
        )

        self.notifications.append(
            {
                "type":
                    "human.requested",

                "process_id":
                    event.source,

                "question":
                    question
            }
        )

        print()
        print(
            "[HUMAN INPUT REQUIRED]"
        )

        print(question)

        print()

    def get_notifications(
        self
    ):

        return list(
            self.notifications
        )

    def clear_notifications(
        self
    ):

        self.notifications.clear()

    def get_conversation(
        self,
        conversation_id
    ):

        return (
            self.memory_manager
            .get_conversation(
                conversation_id
            )
        )

    def get_process(
        self,
        process_id
    ):

        return (
            self.memory_manager
            .get_process(
                process_id
            )
        )