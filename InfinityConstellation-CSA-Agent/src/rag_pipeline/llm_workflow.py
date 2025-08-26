from typing import Any

class LLMWorkflow:
    def __init__(self, model_backend: str = "gpt5"):
        self.backend = model_backend

    def run_task(self, prompt: str) -> str:
        # Placeholder: call the selected LLM backend
        return f"[{self.backend} response] for prompt: {prompt}"