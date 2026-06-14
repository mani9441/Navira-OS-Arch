from resources.capability_provider import (
    CapabilityProvider
)

from resources.memory_provider import (
    MemoryProvider
)

from resources.file_provider import (
    FileProvider
)

from resources.database_provider import (
    DatabaseProvider
)

from resources.llm_provider import (
    LLMProvider
)


class ResourceManager:

    def __init__(
        self,
        capability_registry,
        memory_manager
    ):

        self.capabilities = (
            CapabilityProvider(
                capability_registry
            )
        )

        self.memory = (
            MemoryProvider(
                memory_manager
            )
        )

        self.files = (
            FileProvider()
        )

        self.databases = (
            DatabaseProvider()
        )

        self.llms = (
            LLMProvider()
        )

    def get_capability(
        self,
        capability_name
    ):

        return self.capabilities.get(
            capability_name
        )

    def get_memory(self):

        return self.memory.get()

    def get_file(
        self,
        file_id
    ):

        return self.files.get(
            file_id
        )

    def get_database(
        self,
        database_name
    ):

        return self.databases.get(
            database_name
        )

    def get_llm(
        self,
        model_name
    ):

        return self.llms.get(
            model_name
        )