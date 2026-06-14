from .response import (
    Response
)

from runtime.strategy_evaluator import (
    ExecutionStrategy
)


class ConversationManager:

    def __init__(
        self,
        kernel,
        router,
        parser,
        context_engine
    ):

        self.kernel = kernel

        self.router = router

        self.parser = parser

        self.context_engine = context_engine

    async def handle(
        self,
        message
    ):
        # Assemble the execution context using the context engine
        execution_context = (
            self.context_engine.assemble(
                query=message.content,
                user_id=message.user_id,
                conversation_id=message.conversation_id
            )
        )

        # Pass execution_context.query into the strategy evaluator (router)
        strategy = self.router.route(
            execution_context.query
        )

        if (
            strategy
            == ExecutionStrategy.CAPABILITY
        ):

            # Updated to use execution_context.query
            capability = (
                self.parser.extract_capability(
                    execution_context.query
                )
            )

            if capability == "weather":

                # Updated to use execution_context.query
                city = (
                    self.parser.extract_city(
                        execution_context.query
                    )
                )

                process_id = (
                    await self.kernel.spawn_capability(
                        "weather",
                        {
                            "city": city
                        }
                    )
                )

                return Response(
                    success=True,
                    message=(
                        "Weather process started"
                    ),
                    data={
                        "process_id": process_id
                    }
                )

        return Response(
            success=True,
            message=(
                "Conversation handled"
            )
        )