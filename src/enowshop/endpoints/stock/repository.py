
# Create repository for stock

# Path: src/enowshop/endpoints/stock/repository.py

from enowshop.infrastructure.models.models.stock import Stock
from enowshop.infrastructure.repositories.repository import SqlRepository
from sqlalchemy import select, update, func

class StockRepository(SqlRepository):
    model=Stock

    async def get_all_stock(self, params: dict) -> tuple:
        async with self.session_factory() as session:
            query = select(self.model).limit(params.get('limit')).offset(params.get('offset'))            
            total = await session.execute(select([func.count(self.model.id)]).select_from(self.model))
            results = await session.execute(query)
            total = total.scalar()
            results = results.scalars().all()
            return results, total

    async def get_stock_by_uuid(self, stock_uuid: str) -> Stock:
         async with self.session_factory() as session:
            return session.query(Stock).filter(Stock.uuid == stock_uuid).first()

    async def update_by_uuid(self, pk, values):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.uuid == pk).values(**values))
            await session.commit()

    async def soft_delete_by_uuid(self, pk):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.uuid == pk).values(is_active=False))
            await session.commit()
    
    async def get_stock_by_produc_id(self, product_id: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.product_id == product_id).where(self.model.quantity != 0).order_by(self.model.created_at))
            results = result.scalars().all()
            return results
