
from typing import Dict
from enowshop.infrastructure.models.models.comments import Comments
from enowshop.infrastructure.repositories.repository import SqlRepository
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload, load_only


class CommentsRepository(SqlRepository):
    model = Comments

    async def get_all_comments_paginated(self, params: Dict, product_id: int):
         async with self.session_factory() as session:
            query = select(Comments).where(Comments.product_id == product_id).options(
                selectinload(Comments.user)).limit(params.get('limit')).offset(params.get('offset'))
            total = await session.execute(select([func.count(Comments.id)]).where(Comments.product_id == product_id))
            results = await session.execute(query)

            total = total.scalar()
            results = results.scalars().all()
            return results, total