from runtime.execution_context import (
    ExecutionContext
)


class ContextBuilder:

    def __init__(
        self,
        memory_manager,
        process_manager
    ):

        self.memory_manager = (
            memory_manager
        )

        self.process_manager = (
            process_manager
        )

    def build(
        self,
        query,
        user_id,
        conversation_id
    ):

        conversation_history = (
            self.memory_manager
            .conversation
            .get(conversation_id)
        )

        active_processes = [

            process.to_dict()

            for process in
            self.process_manager.list()
        ]

        global_context = (
            self.memory_manager
            .global_memory
            .all()
        )

        return ExecutionContext(
            query=query,
            user_id=user_id,
            conversation_id=conversation_id,
            conversation_history=
                conversation_history,
            global_context=
                global_context,
            active_processes=
                active_processes
        )