import pytest
import datetime
from src.state.agent_state import AgentState

def test_initial_state():
    state = AgentState()
    snapshot = state.export_state()

    assert "conversation_id" in snapshot
    assert isinstance(snapshot["created_at"], str)
    assert snapshot["messages"] == []
    assert snapshot["context"] == {}
    assert snapshot["current_task"] is None
    assert snapshot["assigned_agent"] is None

def test_add_message():
    state = AgentState()
    state.add_message("user", "Hello world")

    assert len(state.messages) == 1
    msg = state.messages[0]
    assert msg["role"] == "user"
    assert msg["content"] == "Hello world"
    assert "timestamp" in msg

def test_set_task_and_agent():
    state = AgentState()
    state.set_task("pricing_query", "customer_support_agent")

    assert state.current_task == "pricing_query"
    assert state.assigned_agent == "customer_support_agent"

def test_update_context():
    state = AgentState()
    state.update_context("priority", "high")

    assert "priority" in state.context
    assert state.context["priority"] == "high"

def test_export_state_consistency():
    state = AgentState()
    state.add_message("system", "Welcome")
    state.set_task("init", "system_agent")
    state.update_context("session_active", True)

    snapshot = state.export_state()

    assert snapshot["messages"][0]["content"] == "Welcome"
    assert snapshot["current_task"] == "init"
    assert snapshot["assigned_agent"] == "system_agent"
    assert snapshot["context"]["session_active"] is True

def test_timestamps_update():
    state = AgentState()
    created_at = state.created_at
    state.add_message("user", "Test update")
    assert state.last_updated >= created_at