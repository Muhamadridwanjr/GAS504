"""Favorite indicator manager."""
from src.db.repositories.favorite_repo import FavoriteRepo

class FavoritesManager:
    def __init__(self, repo: FavoriteRepo): self.repo = repo
    async def list_favorites(self, user_id): return await self.repo.list_by_user(user_id)
    async def add_favorite(self, user_id, indicator): return await self.repo.add(user_id, indicator)
    async def remove_favorite(self, user_id, indicator): return await self.repo.remove(user_id, indicator)
