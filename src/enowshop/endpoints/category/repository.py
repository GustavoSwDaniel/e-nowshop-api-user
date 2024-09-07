from enowshop.infrastructure.models.models.category import Category
from enowshop.infrastructure.repositories.repository import SqlRepository


class CategoryRepository(SqlRepository):
    model = Category
