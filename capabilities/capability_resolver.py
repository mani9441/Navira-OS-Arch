# capabilities/capability_resolver.py
import json
from typing import Tuple, Dict, Any, List
from llms.llm import get_llm

class CapabilityResolver:
    def __init__(self, capability_registry, vector_db_client, top_k: int = 3):
        self.registry = capability_registry
        self.vector_db = vector_db_client
        self.top_k = top_k
        self.llm = get_llm()

    async def resolve(self, context) -> Tuple[str, Dict[str, Any]]:
        """
        Analyzes the query using Embeddings + LLM Classification.
        Returns the winning capability name and its parsed input arguments.
        """
        query = context.query if hasattr(context, "query") else context.get("query", "")
        if not query:
            raise ValueError("Context query is empty. Cannot resolve capability.")

        # ─── STAGE 1: SEMANTIC RETRIEVAL (TOP-K CANDIDATES) ───
        top_k_names: List[str] = await self.vector_db.search(query=query, limit=self.top_k)
        if not top_k_names:
            raise ValueError("No matching capabilities found in Vector DB.")

        # Build a structured list of schema definitions for the LLM to inspect
        # Build a structured list of schema definitions for the LLM to inspect
        candidate_manifests = []
        for name in top_k_names:
            cap = self.registry.get(name)
            
            # Fallback Check: If direct lookup missed, scan instances manually by class name matching
            if not cap:
                for active_cap in self.registry.list_all():
                    if active_cap.__class__.__name__ == name:
                        cap = active_cap
                        break

            if cap:
                candidate_manifests.append({
                    "name": cap.name, # Ensure the LLM gets the true configured target name property
                    "description": cap.description,
                    "input_schema": cap.input_schema
                })
            else:
                print(f"[OS KERNEL WARNING] Local lookup completely missed for signature key: '{name}'")

        if not candidate_manifests:
            raise ValueError(f"Top-K candidates {top_k_names} found in Vector DB are missing from the registry.")
    
        # ─── STAGE 2: LLM CLASSIFICATION & EXTRACTION ───
        # We ask for a strict JSON payload back instead of letting the LLM trigger a functional tool call.
        # ─── STAGE 2: HARDENED LLM CLASSIFICATION & EXTRACTION ───
        system_prompt = (
            "You are the structural routing and parameter extraction kernel of a secure OS.\n"
            "Your job is to analyze the user's raw query, match it against candidate capability schemas, "
            "and output a strict JSON object mapping parameters.\n\n"
            
            "CRITICAL EXTRACTION SAFEGUARDS:\n"
            "1. ONLY extract parameters explicitly mentioned or clearly implied by the user's specific text string.\n"
            "2. DO NOT hallucinate, guess, or invent default parameters (e.g., Never default a missing location to 'London' or 'Delhi' unless explicitly stated).\n"
            "3. If a field is missing, unclear, or consists of invalid placeholders (like '--', 'somewhere', 'nowhere', '?'), OMIT that key from the arguments payload completely.\n"
            "4. If a vital required field is missing from the query text, leave the 'arguments' object entirely empty: {}.\n\n"
            
            "Your output must be a single, valid JSON object matching this exact shape, with no trailing prose:\n"
            "{\n"
            '  "selected_capability": "capability_name_here",\n'
            '  "arguments": {}\n'
            "}"
        )

        user_content = (
            f"User Query: '{query}'\n\n"
            f"Candidate Capability Schemas:\n"
            f"{json.dumps(candidate_manifests, indent=2)}"
        )

        # Call the LLM (Using structural/json extraction features depending on your LLM API)
        llm_response = await self.llm.chat(
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
            response_format={"type": "json_object"} # Guarantees a clean JSON block back
        )

        # ─── STEP 3: PARSE STRIPPED INTERMEDIARY PAYLOAD ───
        try:
            decision = json.loads(llm_response.content)
            winning_name = decision.get("selected_capability")
            extracted_args = decision.get("arguments", {})
            
            # Sanity double-check: ensure the LLM didn't hallucinate a capability name out of the Top-K bound
            if winning_name in top_k_names:
                print(f"[OS KERNEL] Selected capability: '{winning_name}' with args: {extracted_args}")
                return winning_name, extracted_args
        except (json.JSONDecodeError, KeyError, TypeError):
            print("[OS KERNEL] Router failed parsing LLM classification block. Using fallback.")

        # Fallback clause to protect runtime execution if the model outputs something invalid
        fallback_winner = top_k_names[0]
        print(f"[OS KERNEL] Falling back to Top-1 Vector match: '{fallback_winner}'")
        return fallback_winner, {}