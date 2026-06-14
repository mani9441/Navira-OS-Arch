class StateStore:

    def __init__(self):

        self._states = {}

    def save(self, process_id: str, state: dict):

        self._states[process_id] = state

    def load(self, process_id: str):

        return self._states.get(process_id)

    def delete(self, process_id: str):

        if process_id in self._states:
            del self._states[process_id]

    def exists(self, process_id: str):

        return process_id in self._states

    def all_states(self):

        return self._states