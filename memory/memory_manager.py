from collections import defaultdict


class MemoryManager:

    def __init__(self):

        self.conversations = (
            defaultdict(list)
        )

        self.process_memory = {}

        self.working_memory = (
            defaultdict(dict)
        )

    # ----------------------------------
    # Conversation Memory
    # ----------------------------------

    def store_conversation(
        self,
        conversation_id,
        role,
        content
    ):

        self.conversations[
            conversation_id
        ].append(
            {
                "role":
                    role,

                "content":
                    content
            }
        )

    def get_conversation(
        self,
        conversation_id
    ):

        return list(

            self.conversations.get(
                conversation_id,
                []
            )

        )

    def clear_conversation(
        self,
        conversation_id
    ):

        self.conversations.pop(
            conversation_id,
            None
        )

    # ----------------------------------
    # Process Memory
    # ----------------------------------

    def store_process(
        self,
        process_id,
        data
    ):

        self.process_memory[
            process_id
        ] = data

    def get_process(
        self,
        process_id
    ):

        return self.process_memory.get(
            process_id
        )

    def delete_process(
        self,
        process_id
    ):

        self.process_memory.pop(
            process_id,
            None
        )

    # ----------------------------------
    # Working Memory
    # ----------------------------------

    def set_working_memory(
        self,
        process_id,
        key,
        value
    ):

        self.working_memory[
            process_id
        ][key] = value

    def get_working_memory(
        self,
        process_id,
        key,
        default=None
    ):

        return (

            self.working_memory
            .get(
                process_id,
                {}
            )
            .get(
                key,
                default
            )

        )

    def get_all_working_memory(
        self,
        process_id
    ):

        return dict(

            self.working_memory.get(
                process_id,
                {}
            )

        )

    def delete_working_memory(
        self,
        process_id,
        key
    ):

        if process_id in (
            self.working_memory
        ):

            self.working_memory[
                process_id
            ].pop(
                key,
                None
            )

    def clear_working_memory(
        self,
        process_id
    ):

        self.working_memory.pop(
            process_id,
            None
        )