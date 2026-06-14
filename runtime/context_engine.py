from runtime.context_builder import (
    ContextBuilder
)


class ContextEngine:

    def __init__(
        self,
        memory_manager,
        process_manager
    ):

        self.builder = (
            ContextBuilder(
                memory_manager,
                process_manager
            )
        )

    def assemble(
        self,
        query,
        user_id,
        conversation_id
    ):

        return self.builder.build(
            query=query,
            user_id=user_id,
            conversation_id=
                conversation_id
        )
    