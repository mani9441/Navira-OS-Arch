from runtime.process import (
    ProcessType
)


class ExecutionResolver:

    def resolve(
        self,
        context
    ):

        query = (
            context.inputs
            .get("query", "")
            .lower()
        )

        # Team Requests

        if any(
            keyword in query
            for keyword in [
                "research",
                "investigate",
                "analyze",
                "compare"
            ]
        ):

            return {
                "process_type":
                    ProcessType.TEAM
            }

        # Workflow Requests

        if any(
            keyword in query
            for keyword in [
                "workflow",
                "process",
                "irrigation",
                "automation"
            ]
        ):

            return {
                "process_type":
                    ProcessType.WORKFLOW
            }

        # Everything else

        return {
            "process_type":
                ProcessType.CAPABILITY
        }