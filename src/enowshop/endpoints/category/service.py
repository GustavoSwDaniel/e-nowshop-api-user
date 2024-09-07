from enowshop.endpoints.category.repository import CategoryRepository


class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository

    async def create_category(self, category):
        return await self.category_repository.create(category)

    async def get_category_by_uuid(self, category_id: str):
        return await self.category_repository.filter_by({'uuid': category_id})

    async def get_categories(self):
        return await self.category_repository.get_all()
