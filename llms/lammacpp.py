import asyncio
import json
import os
import re
from dataclasses import dataclass

import requests

from .base import BaseLLM

from dotenv import load_dotenv

load_dotenv()
# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LLAMACPP_URL = os.getenv("LLAMACPP_URL", "http://localhost:8080")


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def extract_json(text: str) -> str:
    """
    Extract JSON content from a Markdown code block.

    Example:
    ```json
    {"key": "value"}
    ```

    If no JSON code block is found, returns the original text.
    """
    text = text.strip()

    match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        flags=re.DOTALL,
    )

    if match:
        return match.group(1)

    return text


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class DummyLLMResult:
    """
    Lightweight wrapper that mimics LangChain-style responses
    so downstream code can access `response.content`.
    """
    content: str


# ---------------------------------------------------------------------------
# Llama.cpp LLM Implementation
# ---------------------------------------------------------------------------

class LlamaCppLLM(BaseLLM):
    def __init__(
        self,
        base_url: str = LLAMACPP_URL,
        n_predict: int = 512,
        temperature: float = 0.2,
        top_p: float = 0.9,
    ):
        self.base_url = base_url
        self.n_predict = n_predict
        self.temperature = temperature
        self.top_p = top_p

    async def ainvoke(self, prompt: str) -> DummyLLMResult:
        """
        Async wrapper around the synchronous generate() method.
        Executes generation in a background thread.
        """
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            self.generate,
            prompt,
        )

        return DummyLLMResult(content=result)

    def generate(
        self,
        prompt: str,
        stream: bool = False,
        on_token=None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text from the model.

        Args:
            prompt: Input prompt.
            stream: Whether to stream tokens.
            on_token: Optional callback for streamed tokens.
            max_tokens: Optional override for output token count.

        Returns:
            Generated text.
        """

        n_predict = max_tokens if max_tokens is not None else self.n_predict

        if stream:
            return self._generate_stream(
                prompt=prompt,
                on_token=on_token,
                max_tokens=n_predict,
            )

        response = requests.post(
            f"{self.base_url}/completion",
            json={
                "prompt": prompt,
                "n_predict": n_predict,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": False,
                "stop": ["User:", "<|im_end|>"],
            },
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

        return data.get("content", "")

    def _generate_stream(
        self,
        prompt: str,
        on_token=None,
    ) -> str:
        """
        Stream tokens from llama.cpp using Server-Sent Events (SSE).

        Args:
            prompt: Input prompt.
            on_token: Callback invoked for every token received.

        Returns:
            Full generated text.
        """
        response = requests.post(
            f"{self.base_url}/completion",
            json={
                "prompt": prompt,
                "n_predict": self.n_predict,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "stream": True,
                "stop": ["User:", "<|im_end|>"],
            },
            stream=True,
            timeout=120,
        )

        response.raise_for_status()

        full_text = ""

        for line in response.iter_lines():
            if not line:
                continue

            decoded = line.decode("utf-8")

            if not decoded.startswith("data:"):
                continue

            payload = decoded.removeprefix("data:").strip()

            if payload == "[DONE]":
                break

            try:
                parsed = json.loads(payload)
                token = parsed.get("content", "")

                if not token:
                    continue

                full_text += token

                if on_token:
                    on_token(token)

            except Exception:
                continue

        return full_text

    def generate_json(self, prompt: str, **kwargs) -> dict:
        """
        Generate structured JSON output.

        The model is expected to return JSON, optionally wrapped
        inside Markdown code fences.

        Args:
            prompt: Input prompt.

        Returns:
            Parsed JSON dictionary.
        """
        raw_output = self.generate(prompt, **kwargs)
        clean_output = extract_json(raw_output)

        return json.loads(clean_output)
    
    def embed(self, text: str) -> list[float]:
        """
        Request raw semantic matrix vectors from the native llama-server endpoint.
        """
        try:
            response = requests.post(
                f"{self.base_url}/embedding",
                json={"content": text},
                timeout=60, 
            )
            response.raise_for_status()
            data = response.json()
            
            # --- ROBUST TYPE PARSING ENGINE ---
            
            # Scenario A: Payload is a direct dictionary wrapper
            if isinstance(data, dict):
                # Check for native llama-server key 'embedding'
                if "embedding" in data:
                    embedding_data = data["embedding"]
                    # If it's a list of dicts (e.g., [{'embedding': [...]}]), unpack it
                    if isinstance(embedding_data, list) and len(embedding_data) > 0 and isinstance(embedding_data[0], dict):
                        return embedding_data[0].get("embedding", [])
                    return embedding_data
                
                # Check for OpenAI-compatible route schemas ('data': [{'embedding': [...]}]),
                if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                    return data["data"][0].get("embedding", [])

            # Scenario B: Payload is a raw list from the server
            if isinstance(data, list) and len(data) > 0:
                # If it's a list of dict objects like [{'embedding': [...]}]
                if isinstance(data[0], dict):
                    return data[0].get("embedding", [])
                # If it's already a direct list of floating point values
                return data
                
            print(f"[WARNING] Unhandled embedding payload format structural shape: {type(data)}")
            return []
            
        except Exception as e:
            print(f"[LLAMACPP ERROR] Failed generating vectors via HTTP: {e}")
            raise e
        

    async def chat(self, system: str, messages: list, response_format: dict = None) -> DummyLLMResult:
        """
        Formats structured system and user prompts into a standard ChatML template 
        compatible with Qwen2.5-Instruct architecture sequences.
        """
        # 1. Build a clean ChatML string format
        formatted_prompt = f"<|im_start|>system\n{system}<|im_end|>\n"
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted_prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
            
        formatted_prompt += "<|im_start|>assistant\n"

        # 2. Forward the compiled string to your background thread executor
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            self.generate,
            formatted_prompt,
        )

        return DummyLLMResult(content=result)





# # Example Usage

# response = llm.generate(prompt) # Normal

# # Stream
# response = llm.generate(
#     prompt,
#     stream=True,
#     on_token=lambda token: print(
#         token,
#         end="",
#         flush=True
#     )
# ) 