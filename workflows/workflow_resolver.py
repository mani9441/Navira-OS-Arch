class WorkflowResolver:

    def __init__(
        self,
        workflow_registry
    ):
        self.workflow_registry = (
            workflow_registry
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

        if "irrigation" in query:
            return self.workflow_registry.get(
                "crop_irrigation"
            )

        if "sales" in query:
            return self.workflow_registry.get(
                "sales"
            )

        if "support" in query:
            return self.workflow_registry.get(
                "customer_support"
            )

        raise ValueError(
            "No workflow found"
        )