from teams.base_team import (
    BaseTeam
)

from teams.research_team.research_lead import (
    ResearchLead
)


class ResearchTeam(
    BaseTeam
):

    def __init__(self):

        self.lead = (
            ResearchLead()
        )

    async def execute(
        self,
        context
    ):

        topic = (
            context.get_input(
                "topic"
            )
        )

        result = (
            await self.lead.execute(
                topic
            )
        )

        return result