# capabilities/registry/__init__.py
from  .capability_registry import CapabilityRegistry
from database.vector_db_client import VectorDBClient
from llms.llm import get_llm

# Explicitly import your capabilities
from capabilities.capabilities.weather.weather_capability import WeatherCapability
from capabilities.capabilities.email.gmail_capability import GmailCapability


# Initialize our infrastructure singletons
capability_registry = CapabilityRegistry()
vector_db = VectorDBClient()

# Get your configured LlamaCppLLM instance
llm_instance = get_llm()

# Inject the LLM into the vector client so it can access the .embed() method
vector_db.set_llm(llm_instance)


# Core system manifest array
MANIFEST = [
    WeatherCapability(),
    GmailCapability(),
    ]

# 1. Synchronously populate your local RAM registry right on import
for capability in MANIFEST:
    capability_registry.register(capability)

# 2. Expose an explicit async lifecycle method for the database sync
async def initialize_and_sync_inventory():
    """Syncs the pre-registered manifest entries directly with the database footprint."""
    print("--- Beginning Capabilities Vector DB Sync ---")
    
    for capability in MANIFEST:
        footprint = capability.to_embedding_text()
        await vector_db.sync_capability(name=capability.name, semantic_text=footprint)
        
    print("--- Capabilities Inventory System Ready ---")

# usage 
# await initialize_and_sync_inventory()