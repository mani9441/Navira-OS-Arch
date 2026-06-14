from teams.research_team.search_specialist import (
    SearchSpecialist
)

from teams.research_team.analysis_specialist import (
    AnalysisSpecialist
)

from teams.research_team.report_specialist import (
    ReportSpecialist
)


class ResearchLead:

    def __init__(self):

        self.search = (
            SearchSpecialist()
        )

        self.analysis = (
            AnalysisSpecialist()
        )

        self.report = (
            ReportSpecialist()
        )

    async def execute(
        self,
        topic
    ):

        findings = (
            await self.search.execute(
                topic
            )
        )

        analysis = (
            await self.analysis.execute(
                findings
            )
        )

        report = (
            await self.report.execute(
                analysis
            )
        )

        return {
            "topic":
                topic,

            "report":
                report
        }