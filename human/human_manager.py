import uuid
from datetime import datetime
from human.human_request import HumanRequest


class HumanManager:

    def __init__(
        self,
        event_manager
    ):

        self.event_manager = (
            event_manager
        )

        self.requests = {}

        self.process_requests = {}

    async def ask(self, process_id, question):
        request_id = str(uuid.uuid4())

        request = HumanRequest(
            request_id=request_id,
            process_id=process_id,
            question=question,
            status="pending",
            created_at=datetime.utcnow(),
        )

        self.requests[request_id] = request
        self.process_requests[process_id] = request_id

        await self.event_manager.publish(
            event_type=
                "human.requested",

            source=
                process_id,

            payload={
                "request_id":
                    request_id,

                "question":
                    question
            }
        )

        return request

    async def respond(self, request_id, response):
        request = self.requests.get(request_id)

        if request is None:
            raise ValueError(f"Request '{request_id}' not found")

        request.response = response
        request.status = "answered"
        request.answered_at = datetime.utcnow()

        await self.event_manager.publish(
            event_type=
                "human.responded",

            source=
                request.process_id,

            payload={
                "request_id":
                    request_id,

                "response":
                    response
            }
        )

        return request

    def get_request(self, request_id):
        return self.requests.get(request_id)

    def get_by_process(self, process_id):
        request_id = self.process_requests.get(process_id)

        if request_id is None:
            return None

        return self.requests.get(request_id)

    def get_response(self, request_id):
        request = self.requests.get(request_id)

        if request is None:
            return None

        return request.response

    def pending(self):
        return [
            request
            for request in self.requests.values()
            if request.status == "pending"
        ]

    def answered(self):
        return [
            request
            for request in self.requests.values()
            if request.status == "answered"
        ]