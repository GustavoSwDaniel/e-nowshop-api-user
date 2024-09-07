
from typing import List

from sqlalchemy import select
from enowshop.infrastructure.models.models.users import Users
from enowshop.infrastructure.repositories.nosql_repository import NosqlRepository
from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop.infrastructure.models.models.users_address import UserAddress
from sqlalchemy.orm import selectinload

from exception import RepositoryException
from enowshop.infrastructure.models.models.carts import Cart
from enowshop.infrastructure.models.models.cart_itens import CartItens
from enowshop.infrastructure.models.models.stock import Stock

class UserRepository(SqlRepository):
    model = Users

    async def filter_by_with_address(self, uuid: str) -> Users:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).options(selectinload(Users.user_address))
                .where(self.model.uuid == uuid)
                .where(self.model.user_address.any(UserAddress.main== True)))
            user = result.scalars().first()
            if not user:
                raise RepositoryException('User does not found')
            return user

class CarsRepository(SqlRepository):
    model = Cart

    async def get_cart(self, user_id: int) -> List[model]:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(self.model.expired == False)
                                           .where(self.model.user_id == user_id)
                                           .options(selectinload(Cart.user))
                                           .options(selectinload(Cart.cart_items)))
            return result.scalars().first()
    
    async def expirate_cart(self, pk):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.id == pk))
            cart = result.scalars().first()
            cart.expired = True
            await session.commit()
    
        
    async def get_car_by_user_id(self, user_id: int) -> model:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(Cart.user_id == user_id)
                                           .where(Cart.expired == False))
            return result.scalars().first()

class CartItensRepository(SqlRepository):
    model = CartItens

    async def change_quantity_item_in_car(self, cart_id: str, item_uuid: str, new_quantity: int) -> None:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(self.model.product_id == item_uuid).where(self.model.cart_id == cart_id))
            item = result.scalars().first()
            if not item:
                raise RepositoryException('Item does not found')
            item.quantity = new_quantity
            await session.commit()
    
    async def remove_item_from_car(self, item_uuid: str, cart_id: str) -> None:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(self.model.product_id == item_uuid)
                                           .where(self.model.cart_id == cart_id))
            item = result.scalars().first()
            if not item:
                raise RepositoryException('Item does not found')
            await session.delete(item)
            await session.commit()

    async def add_item_in_car(self, data: dict, user_uuid: str) -> None:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(self.model.product_id == data['product_id']))
            item = result.scalars().first()
            if item:
                item.quantity += data['quantity']
                await session.commit()
            else:
                await session.execute(self.model.insert().values(**data))
                await session.commit()

    async def get_cart_items_by_cart_id(self, cart_id: int) -> List[model]:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(self.model.cart_id == cart_id))
            return result.scalars().all()

    
class StockRepository(SqlRepository):
    model = Stock

    async def get_stock_by_uuid(self, uuid: str) -> CartItens:
        return await self.get(uuid)
