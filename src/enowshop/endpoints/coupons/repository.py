
from datetime import datetime
from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop.infrastructure.models.models.coupons import Coupons
from enowshop.infrastructure.models.models.coupons_products import CouponsProducts
from sqlalchemy import select


class CouponsRepository(SqlRepository):
    model = Coupons

    async def check_coupon_exists(self, code: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).
                where(self.model.code == code).where(self.model.expiration_date >= datetime.now()))
            return result.scalars().first()


class CouponsProductsRepository(SqlRepository):
    model = CouponsProducts

    async def bulk_create(self, data):
        async with self.session_factory() as session:
            model = session.add_all([self.model(**produc_coupons) for produc_coupons in data])
            await session.commit()
            return model
    