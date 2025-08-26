
import asyncio
from src.massgen_integration.massgen_orchestrator_v005 import create_orchestrator
from src.agents.subagents import SubAgent
from src.agents.customer_support_agent import CustomerSupportAgent
from src.agents.advanced_model_switcher import AdvancedModelSwitcher
from src.db.postgresql_connector import insert_lead, fetch_leads
from src.rag_pipeline.rag_manager import RAGManager
from src.tools.tavily_tool import TavilyTool
from src.tools.agentql_tool import AgentQLTool
from src.tools.jigsawstack_tool import JigsawStackTool

async def main():
    print("=== Infinity Constellation CSA Demo ===")

    # Initialize advanced model switcher
    model_switcher = AdvancedModelSwitcher(models=["gpt5", "claude", "mistral"])
    
    # Initialize DeepAgents
    research_agent = SubAgent(
        name="ResearchAgent",
        model_switcher=model_switcher
    )
    lead_agent = SubAgent(
        name="LeadAgent",
        model_switcher=model_switcher
    )

    # Initialize MassGen orchestrator
    orchestrator = create_orchestrator(agents={
        "research": research_agent,
        "lead": lead_agent
    })

    # Initialize RAG pipeline
    rag_manager = RAGManager()
    rag_manager.load_documents("data/research_docs/demo_docs.json")

    # Initialize external tools
    tavily = TavilyTool()
    agentql = AgentQLTool()
    jigsawstack = JigsawStackTool()

    # Simulate a user query
    user_query = "Find AI startups in healthcare and extract CTO emails"

    print(f"\n[User Query] {user_query}\n")

    # Orchestrator handles query routing to agents
    async for chunk in orchestrator.chat_simple(user_query):
        if chunk.type == "content":
            print(chunk.content, end="")

    # Example: run lead extraction
    leads = lead_agent.run_task(
        task="extract_leads",
        tools=[tavily, agentql, jigsawstack],
        input_query=user_query
    )

    # Insert leads into PostgreSQL
    for lead in leads:
        insert_lead(lead)

    # Fetch and display recent leads
    recent_leads = fetch_leads(limit=5)
    print("\n\n=== Recent Leads Stored in PostgreSQL ===")
    for lead in recent_leads:
        print(lead)

    # RAG pipeline demo
    results = rag_manager.query(user_query)
    print("\n=== RAG Pipeline Results ===")
    for doc in results:
        print(f"{doc['title']}: {doc['summary'][:200]}...")

if __name__ == "__main__":
    asyncio.run(main())
