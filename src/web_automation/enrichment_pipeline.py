import json
from pathlib import Path
from src.db.postgresql_connector import PostgreSQLConnector
from src.rag_pipeline.rag_manager import RAGManager
from src.tools.tavily_tool import TavilyTool
from src.tools.agentql_tool import AgentQLTool
from src.tools.jigsawstack_tool import JigsawStackAIScrape

class EnrichmentPipeline:
    def __init__(self, rag_manager: RAGManager, db_connector: PostgreSQLConnector):
        self.rag = rag_manager
        self.db = db_connector
        self.tavily = TavilyTool()
        self.agentql = AgentQLTool()
        self.jigsawstack = JigsawStackAIScrape()
        self.data_dir = Path("data/research_docs")

    def run(self, queries: list):
        all_docs = []
        for query in queries:
            tavily_results = self.tavily.search(query)
            for res in tavily_results["results"]:
                all_docs.append({"title": f"Tavily: {query}", "content": res, "source": "tavily"})
            agentql_result = self.agentql.execute(f"SELECT * FROM leads WHERE industry='{query}'")
            all_docs.append({"title": f"AgentQL: {query}", "content": json.dumps(agentql_result), "source": "agentql"})
            jigsaw_result = self.jigsawstack.scrape(f"https://example.com/search?q={query}")
            all_docs.append({"title": f"JigsawStack: {query}", "content": jigsaw_result["content"], "source": "jigsawstack"})
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.data_dir / "auto_enriched_docs.json", "w") as f:
            json.dump(all_docs, f, indent=2)
        self.rag.add_documents(all_docs)
        for doc in all_docs:
            self.db.execute("INSERT INTO research_documents (title, content, source) VALUES (%s, %s, %s)",
                            (doc["title"], doc["content"], doc["source"]))