from typing import Dict

from enowshop.infrastructure.models.models.promotion import Promotion

from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from enowshop.endpoints.paginate import paginate
from enowshop.infrastructure.repositories.repository import SqlRepository


class PromotionsRepository(SqlRepository):
    model = Promotion

    async def get_all_paginated(self, params: Dict):
        async with self.session_factory() as session:
            total = await session.execute(select([func.count(self.model.id)]).select_from(self.model))
            result = await session.execute(select(self.model).limit(params.get('limit')).offset(params.get('offset')))
            results = result.scalars().all()
            total = total.scalar()

            return paginate(results, params.get('offset'), total)

    async def update_by_uuid(self, pk, values):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.uuid == pk).values(**values))
            await session.commit()

    async def get_all_products_id_by_promotion(self, promotion_uuid: str) -> dict:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).where(self.model.uuid == promotion_uuid).options(selectinload(self.model.products))
            )

            results = result.scalars().all()

            return paginate(results, 10, results.product)
