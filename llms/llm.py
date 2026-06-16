import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
MODEL = os.getenv("LLM_MODEL", "")
TEMP = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# LlamaCPP specific environment configurations
LLAMACPP_URL = os.getenv("LLAMACPP_URL", "http://localhost:8080")
LLAMACPP_N_PREDICT = int(os.getenv("LLAMACPP_N_PREDICT", "512"))
LLAMACPP_TOP_P = float(os.getenv("LLAMACPP_TOP_P", "0.9"))


def get_llm():
    """
    Universal LLM loader
    """

    # if PROVIDER == "openai":
    #     from langchain_openai import ChatOpenAI 
    #     return ChatOpenAI(
    #         model=MODEL or "gpt-4o-mini",
    #         temperature=TEMP
    #     )

    # elif PROVIDER == "anthropic":
    #     from langchain_anthropic import ChatAnthropic 
    #     return ChatAnthropic(
    #         model=MODEL or "claude-3-5-sonnet-latest",
    #         temperature=TEMP
    #    )

    if PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI 
        return ChatGoogleGenerativeAI(
            model=MODEL or "gemini-1.5-pro",
            temperature=TEMP
        )

    elif PROVIDER == "ollama":
        print("Using Ollama...")
        
        from langchain_ollama import ChatOllama 
        
        return ChatOllama(
            model=MODEL or "llama3",
            temperature=TEMP,
            base_url="http://127.0.0.1:11434" # Change this as needed
        )

    elif PROVIDER == "groq":
        from langchain_groq import ChatGroq
        
        return ChatGroq(
            model=MODEL or "llama-3.1-8b-instant",
            temperature=TEMP,
            # Optional: custom endpoint if you're using a proxy
            # base_url="https://api.groq.com/openai/v1", 
            # api_key="your_api_key_here" # Or set GROQ_API_KEY env var
        )

    elif PROVIDER == "llamacpp":
        print("Using LlamaCPP...")
        
        # Adjust this import path depending on where LlamaCppLLM is located
        # e.g., from .your_module import LlamaCppLLM
        from .lammacpp import LlamaCppLLM
        
        return LlamaCppLLM(
            base_url=LLAMACPP_URL, # Uses MODEL env var if you want to swap endpoints dynamically
            temperature=TEMP,
            n_predict=LLAMACPP_N_PREDICT,
            top_p=LLAMACPP_TOP_P
        )
    
    # elif PROVIDER == "ollama_remote":

    #     from ..LLMs.RemoteOllamaLLM import RemoteOllama

    #     return RemoteOllama(
    #         model=MODEL or "phi3",
    #         temperature=TEMP,
    #         base_url="http://172.23.105.40:8000",
    #         verbose_stream=True
    #     )

    else:
        raise ValueError(f"Unsupported provider: {PROVIDER}")