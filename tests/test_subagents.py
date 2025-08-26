import pytest

from src.agents.subagents import ResearchSubAgent, WritingSubAgent, TodoSubAgent


def test_research_subagent_handles_task():
    agent = ResearchSubAgent()
    out = agent.handle_task("Find context about X", state=None)
    assert isinstance(out, str)
    assert "[ResearchSubAgent]" in out


def test_writing_subagent_handles_task():
    agent = WritingSubAgent()
    out = agent.handle_task("Draft a response about Y", state=None)
    assert isinstance(out, str)
    assert "[WritingSubAgent]" in out


def test_todo_subagent_handles_task():
    agent = TodoSubAgent()
    out = agent.handle_task("Create todos for Z", state=None)
    assert isinstance(out, str)
    assert "[TodoSubAgent]" in out