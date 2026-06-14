class AnalysisSpecialist:

    async def execute(
        self,
        findings
    ):

        analysis = []

        for item in findings:

            analysis.append(
                {
                    "company":
                        item["title"],
                    "insight":
                        "High growth potential"
                }
            )

        return analysis 