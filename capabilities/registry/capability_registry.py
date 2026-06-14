class CapabilityRegistry:
    def __init__(self):
        self.capabilities = {}
        self.keywords = {}
        self.metadata = {}

    def register(self, name: str, capability, keywords: list[str], metadata: dict = None):
        """Registers a capability along with explicit matching keywords and metadata."""
        self.capabilities[name] = capability
        # Store all keywords in lowercase for case-insensitive matching
        self.keywords[name] = [kw.lower() for kw in keywords]
        self.metadata[name] = metadata or {}

    def get(self, name: str):
        return self.capabilities.get(name)

    def exists(self, name: str):
        return name in self.capabilities

    def list(self):
        return list(self.capabilities.keys())