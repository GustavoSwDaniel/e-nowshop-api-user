
from datetime import datetime
from enowshop.infrastructure.models.models.financers import Financers
from enowshop.infrastructure.repositories.repository import SqlRepository
from sqlalchemy import select, update, func
from sqlalchemy import or_


class FinancersRepository(SqlRepository):
    model = Financers

    async def get_financers(self, params: dict):
        async with self.session_factory() as session:
            query = select(self.model).limit(params.get('limit')).offset(params.get('offset'))
            query_total = select([func.count(self.model.id)]).select_from(self.model)

            if params.get('start_date'):
                query = query.where(self.model.created_at >= datetime.strptime(params.get('start_date'), '%Y-%m-%d'))
                query_total = query_total.where(self.model.created_at >= datetime.strptime(params.get('start_date'), '%Y-%m-%d'))
            if params.get('end_date'):
                query = query.where(self.model.created_at <= datetime.strptime(params.get('end_date'), '%Y-%m-%d'))
                query_total = query_total.where(self.model.created_at <= datetime.strptime(params.get('end_date'), '%Y-%m-%d'))

            if params.get('type') == "despesa":
                query = query.where(or_(self.model.type == "despesa", self.model.type == "gasto"))
                query_total = query_total.where(or_(self.model.type == "despesa", self.model.type == "gasto"))
            elif params.get('type') == "receita":
                query = query.where(or_(self.model.type == "venda", self.model.type == "receita"))
                query_total = query_total.where(or_(self.model.type == "venda", self.model.type == "receita"))
            
            total = await session.execute(query_total)
            
            result = await session.execute(query.order_by(self.model.created_at.desc()))
            return result.scalars().all(), total.scalar()
    
    async def get_financers_between_dates(self, params: dict):
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.created_at.between(params.get('start_date'), params.get('end_date')))
            result = await session.execute(query.order_by(self.model.created_at.desc()))
            return result.scalars().all()
    
    async def get_financers_revenue(self, params: dict):
        async with self.session_factory() as session:
            query = select(self.model).where(
                self.model.created_at.between(params.get('start_date'), params.get('end_date')))
            query = query.where(or_(self.model.type == "venda", self.model.type == "receita"))
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_financers_expenses(self, params: dict):
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.created_at.between(params.get('start_date'), params.get('end_date')))
            query = query.where(or_(self.model.type == "despesa", self.model.type == "gasto"))
            result = await session.execute(query)
            
            return result.scalars().all()
        