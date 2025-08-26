

from typing import Any, Dict, Iterable, List

def parse_vote_info(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize vote_info structure. Expected fields (best-effort):
      - agent: agent id/name
      - score: numeric confidence
      - reason: optional explanatory text
    """
    vi = chunk.get("vote_info") or {}
    # best-effort normalization
    return {
        "agent": vi.get("agent", vi.get("name", None)),
        "score": float(vi.get("score", 0.0)) if vi.get("score") is not None else 0.0,
        "reason": vi.get("reason")
    }

async def stream_massgen(orchestrator, query: str, model: str = None, verbosity: str = "minimal", task_type: str = "research_query") -> str:
    """
    Collect the entire stream from orchestrator.chat into a single string.
    Useful for sync-style endpoints and tests.
    """
    buf: List[str] = []
    async for chunk in orchestrator.chat(query, model=model, verbosity=verbosity, task_type=task_type):
        if chunk.get("type") == "content":
            buf.append(chunk.get("content", ""))
        elif chunk.get("type") == "vote_info":
            # append a compact vote info line for debugging
            vi = parse_vote_info(chunk)
            buf.append(f"\n[Vote] agent={vi['agent']} score={vi['score']}\n")
    return "".join(buf)