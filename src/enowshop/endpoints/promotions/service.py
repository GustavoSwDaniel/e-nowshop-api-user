from typing import Dict

from enowshop.endpoints.promotions.repository import PromotionsRepository


class PromotionsService:
    def __init__(self, promotions_repository: PromotionsRepository):
        self.promotions_repo = promotions_repository

    async def register_promotion(self, promotion: Dict):
        return await self.promotions_repo.create(promotion)

    async def get_promotion(self, promotion_id: str):
        return await self.promotions_repo.filter_by({"uuid": promotion_id})

    async def get_promotions(self, params: Dict):
        return await self.promotions_repo.get_all_paginated(params=params)

    async def update_promotion(self, promotion_uuid: str, promotion: Dict):
        return await self.promotions_repo.update_by_uuid(promotion_uuid, promotion)
