"""News query logic."""
from src.db.repositories.news_repo import NewsRepo

class NewsService:
    def __init__(self, repo: NewsRepo):
        self.repo = repo
    async def get_news(self, limit=50):
        rows = await self.repo.get_news(limit)
        return [{"id": r.id, "title": r.title, "source": r.source, "url": r.url,
                 "published_at": str(r.published_at), "summary": r.summary} for r in rows]
