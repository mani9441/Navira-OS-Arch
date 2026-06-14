from runtime.process import (
    ProcessStatus
)


class ProcessManager:

    def __init__(self):

        self.processes = {}

    def register(
        self,
        process
    ):

        self.processes[
            process.id
        ] = process

    def get(
        self,
        process_id
    ):

        return self.processes.get(
            process_id
        )

    def exists(
        self,
        process_id
    ):

        return (
            process_id
            in self.processes
        )

    def update_status(
        self,
        process_id,
        status
    ):

        process = self.get(
            process_id
        )

        if not process:

            raise ValueError(
                f"Process {process_id} not found"
            )

        process.set_status(
            status
        )

        return process

    def remove(
        self,
        process_id
    ):

        if process_id in self.processes:

            del self.processes[
                process_id
            ]

    def list(self):

        return list(
            self.processes.values()
        )

    def list_active(self):

        active = []

        for process in self.processes.values():

            if process.is_active():

                active.append(
                    process
                )

        return active

    def list_completed(self):

        completed = []

        for process in self.processes.values():

            if process.status == (
                ProcessStatus.COMPLETED
            ):

                completed.append(
                    process
                )

        return completed

    def list_failed(self):

        failed = []

        for process in self.processes.values():

            if process.status == (
                ProcessStatus.FAILED
            ):

                failed.append(
                    process
                )

        return failed

    def count(self):

        return len(
            self.processes
        )

    def clear(self):

        self.processes.clear()

    def to_dict(self):

        return [

            process.to_dict()

            for process in
            self.processes.values()
        ]