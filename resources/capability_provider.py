class CapabilityProvider:

    def __init__(
        self,
        capability_registry
    ):

        self.capability_registry = (
            capability_registry
        )

    def get(
        self,
        capability_name
    ):

        capability = (
            self.capability_registry.get(
                capability_name
            )
        )

        if capability is None:

            raise ValueError(
                f"Capability "
                f"'{capability_name}' "
                f"not found"
            )

        return capability