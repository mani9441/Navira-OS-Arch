import json
from pathlib import Path

class CapabilityStateStore:
    def __init__(self, path="storage/capabilities"):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

    def save(self, process_id, state):
        file_path = self.path / f"{process_id}.json"
        with open(file_path, "w") as file:
            json.dump(state, file, indent=4)

    def load(self, process_id):
        file_path = self.path / f"{process_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r") as file:
            return json.load(file)

    def delete(self, process_id):
        file_path = self.path / f"{process_id}.json"
        if file_path.exists():
            file_path.unlink()