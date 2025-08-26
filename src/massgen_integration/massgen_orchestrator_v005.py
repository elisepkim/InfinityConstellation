
import asyncio
import os
import yaml
from typing import AsyncGenerator, Dict, Any, Optional

# Try to import massgen. If missing, provide a lightweight stub so repo runs.
try:
    from massgen import (
        ResponseBackend,
        ClaudeBackend,
        GeminiBackend,
        GrokBackend,
        create_orchestrator,
        create_simple_agent,
        create_expert_agent,
    )
    _HAS_MASSGEN = True
except Exception:
    _HAS_MASSGEN = False

# Import advanced model switcher for direct low-latency calls
try:
    from src.agents.advanced_model_switcher import AdvancedModelSwitcher, GPT5Client, ClaudeClient, MistralAIClient
except Exception:
    # Minimal local fallback implementations if file not present or import fails.
    class GPT5Client:
        def generate(self, prompt: str, verbosity: str = "minimal"):
            return f"[GPT-5 {verbosity}] {prompt[:200]}"

    class ClaudeClient:
        def generate(self, prompt: str, verbosity: str = "minimal"):
            return f"[Claude {verbosity}] {prompt[:200]}"

    class MistralAIClient:
        def generate(self, prompt: str, verbosity: str = "minimal"):
            return f"[Mistral {verbosity}] {prompt[:200]}"

    class AdvancedModelSwitcher:
        def __init__(self):
            self._gpt = GPT5Client()
            self._claude = ClaudeClient()
            self._mistral = MistralAIClient()

        def select_model(self, task_type: str) -> str:
            if task_type in ("structured_data_extraction", "lead_generation"):
                return "gpt5"
            if task_type in ("summarization", "customer_support"):
                return "claude"
            if task_type in ("research_query", "knowledge_discovery"):
                return "mistral"
            return "gpt5"

        def generate(self, prompt: str, task_type: str = "general", verbosity: str = "minimal") -> str:
            m = self.select_model(task_type)
            if m == "gpt5":
                return self._gpt.generate(prompt, verbosity=verbosity)
            if m == "claude":
                return self._claude.generate(prompt, verbosity=verbosity)
            return self._mistral.generate(prompt, verbosity=verbosity)


# Config loader (reads config/massgen.yaml if present)
def _load_config(path: str = "config/massgen.yaml") -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return yaml.safe_load(f) or {}
            except Exception:
                return {}
    return {}

CONFIG = _load_config()

DEFAULT_BACKEND = CONFIG.get("backend", {}).get("default", "gpt5") if isinstance(CONFIG, dict) else "gpt5"
DEFAULT_VERBOSITY = os.getenv("VERBOSITY", CONFIG.get("backend", {}).get("verbosity", "minimal") if isinstance(CONFIG, dict) else "minimal")


class MassGenOrchestratorV005:
    """
    Wrapper for MassGen v0.0.5 orchestrator that:
      - initializes MassGen agents (when available)
      - provides `chat` async generator with streaming chunks and vote_info
      - routes particular subtasks through AdvancedModelSwitcher for low-latency calls
    """

    def __init__(self, backend_name: Optional[str] = None, enable_voting: bool = True, default_verbosity: Optional[str] = None):
        self.backend_name = backend_name or DEFAULT_BACKEND or "gpt5"
        self.enable_voting = enable_voting
        self.default_verbosity = default_verbosity or DEFAULT_VERBOSITY or "minimal"

        # advanced model switcher for direct calls / fast TTFT
        self.model_switcher = AdvancedModelSwitcher()

        if _HAS_MASSGEN:
            # Create actual MassGen backends based on config
            self.backends = self._init_massgen_backends()
            self.agents = {name: create_simple_agent(backend, f"You are {name} agent") for name, backend in self.backends.items()}
            # create orchestrator using v0.0.5 create_orchestrator
            # final_answer_agent and enable_voting are v0.0.5 features
            final_agent = CONFIG.get("orchestrator", {}).get("consensus_agent", "default")
            try:
                self.orchestrator = create_orchestrator(
                    agents=self.agents,
                    final_answer_agent=final_agent,
                    enable_voting=self.enable_voting,
                )
            except Exception:
                # fallback to Orchestrator if create_orchestrator signature differs
                from massgen import Orchestrator, create_orchestrator as _co  # type: ignore
                self.orchestrator = Orchestrator(agents=self.agents)
        else:
            # no massgen available — use stubbed agents list for streaming demo
            self.backends = {}
            self.agents = {}
            self.orchestrator = None

    def _init_massgen_backends(self) -> Dict[str, Any]:
        """
        Initialize MassGen backends. Use configured model keys if available.
        Returns dict: name -> backend instance.
        """
        backends = {}
        # Typical mapping: gpt5 -> ResponseBackend, claude -> ClaudeBackend, mistral->ResponseBackend placeholder
        try:
            if "gpt5" in (CONFIG.get("models") or {}):
                backends["gpt5"] = ResponseBackend()  # generic response backend
            else:
                backends["gpt5"] = ResponseBackend()
        except Exception:
            # if ResponseBackend signature changed, just skip
            backends["gpt5"] = ResponseBackend() if "ResponseBackend" in globals() else None

        try:
            backends["claude"] = ClaudeBackend(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except Exception:
            backends["claude"] = None

        try:
            backends["mistral"] = ResponseBackend()  # placeholder if MistralBackend not provided by massgen
        except Exception:
            backends["mistral"] = None

        try:
            backends["gemini"] = GeminiBackend(api_key=os.getenv("GOOGLE_API_KEY"))
        except Exception:
            backends["gemini"] = None

        # Filter out None entries
        return {k: v for k, v in backends.items() if v is not None}

    async def _stream_from_massgen(self, user_query: str, model_hint: Optional[str], verbosity: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chunks from MassGen orchestrator. If orchestrator absent, yield stubbed chunks.
        """
        if self.orchestrator is None:
            # stub streaming: simulate multi-agent streaming
            agents = ["gpt5", "claude", "mistral"]
            for a in agents:
                # Simulate small network/compute delay
                await asyncio.sleep(0.08)
                content = self.model_switcher.generate(user_query, task_type="research_query", verbosity=verbosity)
                yield {"type": "content", "model": a, "content": content}
                # optionally emit vote_info stub for demonstration
                if self.enable_voting:
                    yield {"type": "vote_info", "vote_info": {"agent": a, "score": 1.0}}
            return

        # If real orchestrator exists, use its streaming API; adapt to chunk interface
        try:
            # massgen orchestrator.chat_simple yields chunks that have `type` and possibly `vote_info`
            async for chunk in self.orchestrator.chat_simple(user_query):
                # Normalize to our public format
                if getattr(chunk, "type", None) == "content":
                    yield {"type": "content", "model": getattr(chunk, "model", None), "content": chunk.content}
                elif hasattr(chunk, "vote_info"):
                    yield {"type": "vote_info", "vote_info": chunk.vote_info}
                else:
                    # fallback: treat as content
                    text = getattr(chunk, "content", str(chunk))
                    yield {"type": "content", "model": None, "content": text}
        except Exception:
            # any error in massgen streaming -> fall back to model_switcher
            content = self.model_switcher.generate(user_query, task_type="research_query", verbosity=verbosity)
            yield {"type": "content", "model": model_hint or "gpt5", "content": content}
            if self.enable_voting:
                yield {"type": "vote_info", "vote_info": {"agent": model_hint or "gpt5", "score": 1.0}}

    async def chat(
        self,
        user_query: str,
        *,
        model: Optional[str] = None,
        verbosity: Optional[str] = None,
        task_type: str = "research_query",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Public async generator. Yields dicts:
          - {"type":"content", "model": "...", "content": "..."}
          - {"type":"vote_info", "vote_info": {...}}
        Parameters:
          - user_query: the user prompt
          - model: optional backend hint (gpt5 / claude / mistral / gemini)
          - verbosity: "minimal" | "balanced" | "verbose"
          - task_type: semantic task hint for model switching
        """
        verbosity = verbosity or self.default_verbosity or "minimal"
        model_hint = (model or self.model_switcher.select_model(task_type)).lower()

        # Step 1: quick primary bypass using low-latency model switcher for first-token speed
        try:
            primary = self.model_switcher.generate(user_query, task_type=task_type, verbosity=verbosity)
            yield {"type": "content", "model": model_hint, "phase": "primary", "content": primary}
        except Exception as e:
            yield {"type": "content", "model": model_hint, "phase": "primary", "content": f"[primary-fallback] {str(e)}"}

        # Step 2: pipe through MassGen orchestrator for multi-agent consensus/streaming
        async for chunk in self._stream_from_massgen(user_query, model_hint, verbosity):
            yield chunk

    # Convenience sync wrapper for quick demos (not streaming)
    async def chat_sync(self, user_query: str, model: Optional[str] = None, verbosity: Optional[str] = None, task_type: str = "research_query") -> str:
        """
        Returns a single concatenated string of streamed content (useful for tests).
        """
        collected = []
        async for out in self.chat(user_query, model=model, verbosity=verbosity, task_type=task_type):
            if out.get("type") == "content":
                collected.append(out.get("content", ""))
        return "".join(collected)
