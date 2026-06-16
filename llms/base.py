class BaseLLM:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def generate_json(self, prompt: str) -> dict:
        raise NotImplementedError

