import uuid
import datetime
from typing import Dict, Any, Optional


class AgentState:
    """Manages state for customer support agent and sub-agents."""

    def __init__(self, conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.created_at = datetime.datetime.utcnow()
        self.last_updated = self.created_at
        self.messages: list[Dict[str, Any]] = []  # conversation history
        self.context: Dict[str, Any] = {}         # shared state
        self.current_task: Optional[str] = None
        self.assigned_agent: Optional[str] = None

    def add_message(self, role: str, content: str) -> None:
        """Append a message to state history."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.messages.append(msg)
        self.last_updated = datetime.datetime.utcnow()

    def set_task(self, task: str, agent: Optional[str] = None) -> None:
        """Assign current task and responsible agent."""
        self.current_task = task
        self.assigned_agent = agent
        self.last_updated = datetime.datetime.utcnow()

    def update_context(self, key: str, value: Any) -> None:
        """Update context dictionary with new info."""
        self.context[key] = value
        self.last_updated = datetime.datetime.utcnow()

    def export_state(self) -> Dict[str, Any]:
        """Return full state snapshot as dict (for DB persistence or API)."""
        return {
            "conversation_id": self.conversation_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "messages": self.messages,
            "context": self.context,
            "current_task": self.current_task,
            "assigned_agent": self.assigned_agent,
        }


# Example DB persistence (if connected to PostgreSQL)
try:
    from src.db.postgresql_connector import get_db_connection
except ImportError:
    get_db_connection = None


def persist_state(state: AgentState) -> None:
    """Persist agent state snapshot into PostgreSQL (if enabled)."""
    if get_db_connection is None:
        print("⚠️ DB connector not available, skipping persistence")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        INSERT INTO csa_query_logs (conversation_id, query, response, created_at)
        VALUES (%s, %s, %s, %s)
    """
    # Save last message only for logging
    if state.messages:
        last_msg = state.messages[-1]
        cur.execute(
            query,
            (
                state.conversation_id,
                last_msg["content"],
                f"Task={state.current_task}, Agent={state.assigned_agent}",
                datetime.datetime.utcnow(),
            ),
        )
        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    # Demo usage
    state = AgentState()
    state.add_message("user", "Hello, I need help with pricing.")
    state.set_task("pricing_query", "customer_support_agent")
    state.update_context("priority", "high")

    print("Snapshot:", state.export_state())

    # Try persisting if DB is available
    persist_state(state)