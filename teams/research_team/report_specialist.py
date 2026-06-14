class ReportSpecialist:

    async def execute(
        self,
        analysis
    ):

        report = []

        report.append(
            "# Research Report"
        )

        report.append("")

        for item in analysis:

            report.append(
                f"- {item['company']}"
            )

            report.append(
                f"  {item['insight']}"
            )

            report.append("")

        return "\n".join(report)