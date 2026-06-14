from runtime.process import Process


class Task:

    def __init__(
        self,
        process: Process,
        executable,
        context: dict
    ):

        self.process = process

        self.executable = executable

        self.context = context