from typing import List, Dict

from sqlalchemy import desc, select, func, extract
from sqlalchemy.orm import selectinload

from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop.infrastructure.models.models.order_items import OrderItems
from enowshop.infrastructure.models.models.orders import Orders
from enowshop.infrastructure.models.models.users import Users
from enowshop.infrastructure.models.models.users_address import UserAddress, State
from enowshop.infrastructure.models.models.products import Products
from enowshop.infrastructure.models.models.category_products import CategoryProducts
from enowshop.infrastructure.models.models.category import Category
from exception import RepositoryException


class OrdersRepository(SqlRepository):
    model = Orders

    async def get_count_total_orders_approvad(self) -> int:
        try:
            async with self.session_factory() as session:
                result = await session.execute(select(func.count()).where(self.model.status == 'approved'))
                return result.scalar()
        except Exception as e:
            raise RepositoryException(str(e))
    
    async def get_sum_total_value_orders_approvaded(self) -> float:
        try:
            async with self.session_factory() as session:
                result = await session.execute(select(func.sum(self.model.total_amount)).where(self.model.status == 'approved'))
                return result.scalar()
        except Exception as e:
            raise RepositoryException(str(e))
    
    @staticmethod
    def mouth_dict(mouth_number: int):
        mouth = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }

        return mouth[mouth_number]
    
    async def get_orders_by_mouth(self) -> List:
        async with self.session_factory() as session:
            result = await session.execute(select([extract('month', self.model.created_at).label('month'), func.count(self.model.id).label('count')]).group_by(extract('month', self.model.created_at)))
            result = result.fetchall()
            sales_per_mouth = {}
            for row in result:
                month = self.mouth_dict(row.month)
                count = row.count
                sales_per_mouth[month] = count
            return sales_per_mouth
    
    async def get_orders_by_states(self) -> List:
        async with self.session_factory() as session:
            result = await session.execute(select([UserAddress.state, func.count(self.model.id).label('count')])
                                           .join(UserAddress, UserAddress.id == Orders.address_id).
                                           group_by('state').order_by(desc('count')))
            result = result.fetchall()
            sales_per_state = {}
            for row in result:
                state = row.state.value
                count = row.count
                sales_per_state[state] = count
            return sales_per_state

    
class OrdersItemsRepository(SqlRepository):
    model = OrderItems
        
    async def count_sales_per_category(self) -> List[Dict]:
        async with self.session_factory() as session:
            results = await session.execute(select([Category.name, func.count(self.model.id).label('count')])
                                                   .join(Products, Products.id == self.model.product_id)
                                                   .join(CategoryProducts, CategoryProducts.product_id == Products.id)
                                                   .join(Category, Category.id == CategoryProducts.category_id).group_by("name").order_by(desc('count')))
            results = results.fetchall()

            category_count = {row[0]: row[1] for row in results}

            return category_count


class ProductsRepository(SqlRepository):
    model = Products

    

class UsersRepository(SqlRepository):
    model = Users

    async def get_count_total_users(self) -> int:
        try:
            async with self.session_factory() as session:
                result = await session.execute(select(func.count()))
                return result.scalar()
        except Exception as e:
            raise RepositoryException(str(e))