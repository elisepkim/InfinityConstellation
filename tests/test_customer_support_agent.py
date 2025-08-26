import pytest

from src.agents.customer_support_agent import CustomerSupportAgent


def test_customer_support_agent_pipeline():
    agent = CustomerSupportAgent()
    result = agent.handle_query("How do I upgrade my plan?")
    assert isinstance(result, dict)

    # Ensure all keys are present
    assert "query" in result
    assert "research" in result
    assert "writing" in result
    assert "todo" in result

    # Ensure values are strings as expected by stubbed subagents
    assert isinstance(result["research"], str)
    assert isinstance(result["writing"], str)
    assert isinstance(result["todo"], str)

    # Quick content sanity checks
    assert "[ResearchSubAgent]" in result["research"]
    assert "[WritingSubAgent]" in result["writing"]
    assert "[TodoSubAgent]" in result["todo"]