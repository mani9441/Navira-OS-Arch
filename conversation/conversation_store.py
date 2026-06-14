class ConversationStore:

    def __init__(self):

        self.conversations = {}

    def append(
        self,
        conversation_id,
        role,
        content
    ):

        if conversation_id not in self.conversations:

            self.conversations[
                conversation_id
            ] = []

        self.conversations[
            conversation_id
        ].append(
            {
                "role": role,
                "content": content
            }
        )

    def get(
        self,
        conversation_id
    ):

        return self.conversations.get(
            conversation_id,
            []
        )