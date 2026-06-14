class HumanQueue:

    def __init__(self):

        self.requests = {}

    def add(
        self,
        request
    ):

        self.requests[
            request.id
        ] = request

        return request.id

    def get(
        self,
        request_id
    ):

        return self.requests.get(
            request_id
        )

    def remove(
        self,
        request_id
    ):

        self.requests.pop(
            request_id,
            None
        )

    def list(self):

        return list(
            self.requests.values()
        )

    def count(self):

        return len(
            self.requests
        )