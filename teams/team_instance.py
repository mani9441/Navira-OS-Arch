class TeamInstance:

    def __init__(
        self,
        team,
        context
    ):

        self.team = team

        self.context = context

    async def execute(self):

        return await self.team.execute(
            self.context
        )