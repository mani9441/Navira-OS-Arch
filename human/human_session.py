class HumanSession:

    def __init__(
        self,
        request
    ):

        self.request = request

        self.response = None

    def submit_response(
        self,
        response
    ):

        self.response = response

    def is_completed(self):

        return (
            self.response
            is not None
        )