class JigsawStackAIScrape:
    def scrape(self, url: str) -> dict:
        return {"url": url, "content": f"Scraped content from {url}", "metadata": {"source": "web"}}