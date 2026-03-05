"""Template CRUD manager."""
from src.db.repositories.template_repo import TemplateRepo

class TemplateManager:
    def __init__(self, repo: TemplateRepo): self.repo = repo
    async def list_templates(self, user_id): return await self.repo.list_by_user(user_id)
    async def get_template(self, user_id, tmpl_id): return await self.repo.get_by_id(user_id, tmpl_id)
    async def create_template(self, user_id, name, layout): return await self.repo.create(user_id, name, layout)
    async def update_template(self, user_id, tmpl_id, **kwargs):
        t = await self.repo.get_by_id(user_id, tmpl_id)
        if not t: return None
        return await self.repo.update(t, **kwargs)
    async def delete_template(self, user_id, tmpl_id):
        t = await self.repo.get_by_id(user_id, tmpl_id)
        if not t: return False
        await self.repo.delete(t); return True
