# capabilities/capability.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Capability(ABC):
    """
    Abstract Base Class for all system capabilities.
    Self-documents safely for both Vector Search footprints and LLM Context injection.
    """
    name: str
    description: str
    
    # Make these optional by providing standard fallback defaults
    category: str = "general_utility"
    version: str = "1.0.0"
    keywords: List[str] = []
    input_schema: Dict[str, Any] = {}

    def to_embedding_text(self) -> str:
        """
        Compiles structural definitions dynamically. Safe against missing metadata fields
        and handles both flat and standard multi-tool capabilities.
        """
        schema = getattr(self, "input_schema", {}) or {}
        properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
        
        # Build parameter summaries cleanly if properties exist
        if properties:
            param_context = ", ".join([
                f"{k}: {v.get('description', '')}" if isinstance(v, dict) else f"{k}: {v}"
                for k, v in properties.items()
            ])
        else:
            param_context = "None"

        # Safely extract optional fields using getattr baseline fallbacks
        category_str = getattr(self, "category", "utility")
        keywords_list = getattr(self, "keywords", [])
        keywords_str = ", ".join(keywords_list) if keywords_list else "None"

        return (
            f"Capability: {self.name} | Category: {category_str}\n"
            f"Description: {self.description}\n"
            f"Keywords: {keywords_str}\n"
            f"Parameters: {param_context}"
        )

    @abstractmethod
    async def execute(self, context: Any, *args, **kwargs) -> Dict[str, Any]:
        """Core programmatic execution path for the tool."""
        pass