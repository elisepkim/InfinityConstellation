import os
import requests
from typing import Literal

VerbosityLevel = Literal["minimal", "balanced", "verbose"]

class GPT5Client:
    """
    GPT-5 wrapper with verbosity control for reasoning + latency tradeoffs.
    """

    def __init__(self, api_key=None, base_url="https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("GPT5_API_KEY")
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
        task_type: str = "general",
        verbosity: VerbosityLevel = "minimal",
    ) -> str:
        """
        Call GPT-5 with configurable verbosity parameter.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}

        payload = {
            "model": "gpt-5",
            "input": prompt,
            # 🔑 Control reasoning depth
            "verbosity": verbosity,                 # "minimal", "balanced", "verbose"
            "reasoning": {"effort": "low" if verbosity == "minimal" else "medium"},
            "decoding": {"strategy": "fast"},
            "response_format": "text",
            "max_output_tokens": 512 if verbosity == "minimal" else 2048,
            "temperature": 0.2 if verbosity == "minimal" else 0.6,
        }

        # Stubbed response for demo
        return f"[GPT-5 {verbosity}] {prompt[:50]}..."
        # If calling API:
        # r = requests.post(f"{self.base_url}/responses", headers=headers, json=payload)
        # return r.json()["output_text"]

        from src.agents.advanced_model_switcher import GPT5Client

def run_demo():
    gpt5 = GPT5Client()

    # Minimal verbosity (fast, low-latency)
    print("\n--- Minimal ---")
    print(gpt5.generate("Summarize this doc", verbosity="minimal"))

    # Balanced verbosity (default reasoning depth)
    print("\n--- Balanced ---")
    print(gpt5.generate("Explain this technical concept", verbosity="balanced"))

    # Verbose mode (step-by-step reasoning, more tokens)
    print("\n--- Verbose ---")
    print(gpt5.generate("Walk me through the solution step by step", verbosity="verbose"))

if __name__ == "__main__":
    run_demo()