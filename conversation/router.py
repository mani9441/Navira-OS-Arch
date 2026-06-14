from runtime.strategy_evaluator import (
    ExecutionStrategy
)


class ConversationRouter:

    def __init__(
        self,
        evaluator
    ):

        self.evaluator = evaluator

    def route(
        self,
        text
    ):

        return self.evaluator.evaluate(
            text
        )