from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import asyncio

from src.massgen_integration.massgen_orchestrator_v005 import MassGenOrchestratorV005
from src.massgen_integration.massgen_tools_v005 import stream_massgen

router = APIRouter()
# instantiate a single orchestrator for the API process (reuse across requests)
_orchestrator = MassGenOrchestratorV005()

VALID_VERBOSITY = {"minimal", "balanced", "verbose"}

def _validate_verbosity(v: Optional[str]) -> str:
    if v is None:
        return _orchestrator.default_verbosity or "minimal"
    if v not in VALID_VERBOSITY:
        raise HTTPException(status_code=400, detail=f"verbosity must be one of {sorted(VALID_VERBOSITY)}")
    return v

@router.get("/chat/stream", summary="Stream responses from the orchestrator")
async def chat_stream(
    prompt: str = Query(..., description="User prompt to send to the orchestrator"),
    model: Optional[str] = Query(None, description="Backend hint (gpt5|claude|mistral|gemini)"),
    verbosity: Optional[str] = Query(None, description="verbosity level: minimal|balanced|verbose"),
    task_type: Optional[str] = Query("research_query", description="Task type hint for model switching"),
):
    """
    Streams content chunks as plain text. Each chunk is sent as a chunked HTTP response (text/plain).
    The very first chunk is a fast primary response from the low-latency model switcher, followed by orchestrator streaming.
    """
    verbosity = _validate_verbosity(verbosity)

    async def _event_stream():
        async for chunk in _orchestrator.chat(prompt, model=model, verbosity=verbosity, task_type=task_type):
            # Only stream content chunks to UI; if vote_info present, stream a short metadata line
            if chunk.get("type") == "content":
                text = chunk.get("content", "")
                # ensure newline separation for streaming clients
                yield text
            elif chunk.get("type") == "vote_info":
                vi = chunk.get("vote_info", {})
                yield f"\n[Vote] agent={vi.get('agent')} score={vi.get('score')}\n"
            else:
                # fallback: try to stringify
                yield str(chunk)

            # tiny sleep to yield cooperatively (helps some WSGI/ASGI servers)
            await asyncio.sleep(0)

    return StreamingResponse(_event_stream(), media_type="text/plain; charset=utf-8")


@router.post("/chat/sync", summary="Synchronous (collected) response")
async def chat_sync(
    prompt: str,
    model: Optional[str] = None,
    verbosity: Optional[str] = None,
    task_type: Optional[str] = "research_query",
):
    """
    Runs the orchestrator and returns the full concatenated response (useful for tests or non-streaming clients).
    """
    verbosity = _validate_verbosity(verbosity)
    out = await stream_massgen(_orchestrator, prompt, model=model, verbosity=verbosity, task_type=task_type)
    return JSONResponse({"prompt": prompt, "model": model or _orchestrator.model_switcher.select_model(task_type), "verbosity": verbosity, "response": out})

 @router.post("/scrape")
async def scrape_endpoint(request: ScrapeRequest):
    result = await scrape_page(request.url, selector=request.selector)
    return result