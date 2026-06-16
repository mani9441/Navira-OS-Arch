# capabilities/capability.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Capability(ABC):
    """
    Abstract Base Class for all system capabilities.
    Self-documents for both Vector Search footprints and LLM Context injection.
    """
    name: str
    description: str
    category: str
    version: str
    keywords: List[str]
    input_schema: Dict[str, Any]

    def to_embedding_text(self) -> str:
        """
        Compiles structural definitions into a dense semantic string block 
        used by the vector storage engine during initialization indexing.
        """
        properties = self.input_schema.get("properties", {})
        param_context = ", ".join([f"{k}: {v.get('description', '')}" for k, v in properties.items()])
        return (
            f"Capability: {self.name} | Category: {self.category}\n"
            f"Description: {self.description}\n"
            f"Keywords: {', '.join(self.keywords)}\n"
            f"Parameters: {param_context}"
        )

    @abstractmethod
    async def execute(self, context: Any, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Core programmatic execution path for the tool."""
        pass