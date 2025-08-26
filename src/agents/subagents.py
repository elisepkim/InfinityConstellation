

from deepagents.sub_agent import _create_task_tool, SubAgent
from deepagents.model import get_default_model
from deepagents.tools import write_todos, write_file, read_file, ls, edit_file
from deepagents.state import DeepAgentState
from typing import List, Dict, Any
from langgraph.prebuilt import create_react_agent


class ResearchSubAgent(SubAgent):
    """Sub-agent for research & knowledge retrieval."""

    def __init__(self, model=None):
        model = model or get_default_model("gpt-5")
        super().__init__("research", model=model)
        self.register_tool(read_file)
        self.register_tool(ls)

    def handle_task(self, query: str, state: DeepAgentState) -> str:
        return f"[ResearchSubAgent] Retrieved context for: {query}"


class WritingSubAgent(SubAgent):
    """Sub-agent for drafting structured responses."""

    def __init__(self, model=None):
        model = model or get_default_model("claude")
        super().__init__("writing", model=model)
        self.register_tool(write_file)
        self.register_tool(edit_file)

    def handle_task(self, query: str, state: DeepAgentState) -> str:
        return f"[WritingSubAgent] Drafted response for: {query}"


class TodoSubAgent(SubAgent):
    """Sub-agent for task & todo management."""

    def __init__(self, model=None):
        model = model or get_default_model("mistral")
        super().__init__("todo", model=model)
        self.register_tool(write_todos)

    def handle_task(self, query: str, state: DeepAgentState) -> str:
        return f"[TodoSubAgent] Created todos for: {query}"


def build_react_agent(tools: List[Any]):
    """Wrap LangGraph ReAct agent with sub-agent tools."""
    return create_react_agent(
        tools=tools,
        model=get_default_model("gemini"),
    )
