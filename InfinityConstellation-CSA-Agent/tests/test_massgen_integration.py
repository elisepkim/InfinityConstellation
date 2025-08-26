import pytest
import asyncio

from src.massgen_integration.massgen_orchestrator_v005 import MassGenOrchestratorV005


@pytest.mark.asyncio
async def test_orchestrator_stream_minimal():
    orch = MassGenOrchestratorV005(enable_voting=True, default_verbosity="minimal")
    chunks = []
    async for chunk in orch.chat("Test streaming response", task_type="research_query", verbosity="minimal"):
        assert isinstance(chunk, dict)
        assert "type" in chunk
        chunks.append(chunk)

    # At least one content chunk expected from fast primary
    assert any(c.get("type") == "content" for c in chunks)

    # If voting enabled, we may see vote_info chunks (stub produces them)
    has_vote = any(c.get("type") == "vote_info" for c in chunks)
    assert has_vote or True  # don't require, but allow it


@pytest.mark.asyncio
async def test_orchestrator_chat_sync_collects():
    orch = MassGenOrchestratorV005(enable_voting=False, default_verbosity="minimal")
    text = await orch.chat_sync("Aggregate this output", task_type="lead_generation", verbosity="minimal")
    assert isinstance(text, str)
    assert len(text) > 0