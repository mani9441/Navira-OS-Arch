class TeamResolver:

    def __init__(
        self,
        team_registry
    ):
        self.team_registry = (
            team_registry
        )

    async def resolve(
        self,
        context
    ):

        query = (
            context.inputs
            .get("query", "")
            .lower()
        )

        if "research" in query:
            return self.team_registry.get(
                "research"
            )

        if "code" in query:
            return self.team_registry.get(
                "coding"
            )

        raise ValueError(
            "No team found"
        )