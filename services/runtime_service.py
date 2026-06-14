class RuntimeService:

    def __init__(
        self,
        dashboard,
        process_queries
    ):

        self.dashboard = dashboard

        self.process_queries = (
            process_queries
        )

    def status(self):

        return self.dashboard.summary()

    def processes(self):

        return (
            self.process_queries
            .all_processes()
        )