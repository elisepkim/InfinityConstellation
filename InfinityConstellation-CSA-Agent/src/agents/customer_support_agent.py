

from typing import Dict
from deepagents.state import DeepAgentState
from .subagents import ResearchSubAgent, WritingSubAgent, TodoSubAgent, build_react_agent


class CustomerSupportAgent:
    """Composite CSA powered by DeepAgents + LangGraph."""

    def __init__(self):
        self.state = DeepAgentState()
        self.research = ResearchSubAgent()
        self.writing = WritingSubAgent()
        self.todo = TodoSubAgent()
        self.react_agent = build_react_agent(
            tools=[
                self.research,
                self.writing,
                self.todo,
            ]
        )

    def handle_query(self, query: str) -> Dict:
        """Main entrypoint for customer queries."""
        self.state.update_context("latest_query", query)

        research_result = self.research.handle_task(query, self.state)
        writing_result = self.writing.handle_task(query, self.state)
        todo_result = self.todo.handle_task(query, self.state)

        return {
            "query": query,
            "research": research_result,
            "writing": writing_result,
            "todo": todo_result,
        }
