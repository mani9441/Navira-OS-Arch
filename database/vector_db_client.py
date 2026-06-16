# database/vector_db_client.py
import hashlib
import numpy as np
from typing import List

class VectorDBClient:
    def __init__(self, llm_instance=None):
        self.llm = llm_instance
        self.storage: List[dict] = []


    def set_llm(self, llm_instance):
        """Links the global engine proxy to this database client adapter."""
        self.llm = llm_instance


    def _generate_text_hash(self, text: str) -> str:
        """Determines if a capability schema text profile has mutated."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()


    def _get_embedding(self, text: str) -> np.ndarray:
        """Pulls mathematical weights from the live local server and pools them into a 1D vector."""
        if self.llm is None:
            raise ValueError("[VECTOR-DB] Core LlamaCppLLM instance is missing inside VectorDBClient.")
        
        raw_weights = self.llm.embed(text)
        if not raw_weights:
            raise ValueError("[VECTOR-DB] The server returned an empty array.")
        
        # Convert to an initial raw numpy matrix
        arr = np.array(raw_weights, dtype=np.float32)
        
        # ─── FIXED: MATRIX POOLING LOGIC ───
        # If the server returns a 2D sequence matrix (e.g., shape [tokens, 2048])
        # we average the token layers along axis 0 to create a unified 1D sentence representation [2048]
        if arr.ndim == 2:
            arr = np.mean(arr, axis=0)
        elif arr.ndim > 2:
            # Fallback wrapper guard for alternative batched outputs
            arr = np.mean(arr.reshape(-1, arr.shape[-1]), axis=0)
            
        return arr


    async def sync_capability(self, name: str, semantic_text: str) -> None:
        """Saves or updates capability vectors based on cache checking."""
        current_hash = self._generate_text_hash(semantic_text)
        existing_record = next((item for item in self.storage if item["name"] == name), None)
        
        if existing_record and existing_record.get("hash") == current_hash:
            return

        print(f"[VECTOR-DB] Content modification found for '{name}'. Embedding via Qwen2.5...")
        vector = self._get_embedding(semantic_text)
        
        # Overwrite previous occurrences safely
        self.storage = [item for item in self.storage if item["name"] != name]
        
        self.storage.append({
            "name": name,
            "text": semantic_text,
            "vector": vector,
            "hash": current_hash
        })
        print(f"[VECTOR-DB] Verified index footprint for '{name}'.")


    async def search(self, query: str, limit: int = 3) -> List[str]:
        """Calculates standard cosine similarities to pick winning contexts."""
        if not self.storage:
            print("[VECTOR-DB] Warning: Vector database storage footprint is completely empty.")
            return []

        # 1. Fetch live weights from llama-server
        query_vector = self._get_embedding(query)
        rankings = []

        print(f"\n[VECTOR-DB DEBUG] Calculating similarity scores for query: '{query}'")

        # 2. Match against all stored capability matrices
        for item in self.storage:
            item_vector = item["vector"]
            
            # True Cosine Similarity Math
            dot_product = np.dot(query_vector, item_vector)
            norm_q = np.linalg.norm(query_vector)
            norm_i = np.linalg.norm(item_vector)
            
            similarity = float(dot_product / (norm_q * norm_i)) if (norm_q and norm_i) else 0.0
            
            print(f" -> Candidate: '{item['name']}' | Raw Cosine Score: {similarity:.4f}")
            rankings.append((item["name"], similarity))

        # 3. Sort descending by match score
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        # --- CRITICAL FILTER FIX ---
        # Instead of filtering out everything strictly, return the top closest match 
        # as long as it has *some* mathematical correlation (> 0.1)
        valid_matches = [name for name, score in rankings if score > 0.1]
        
        if not valid_matches and rankings:
            # Fallback to the absolute highest mathematical node if everything is low
            print(f"[VECTOR-DB] All matches scored very low. Defaulting to best option: '{rankings[0][0]}'")
            return [rankings[0][0]]

        return valid_matches[:limit]
    

