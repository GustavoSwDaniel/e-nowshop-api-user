from datetime import timedelta, datetime
from typing import List, Dict
from enowshop.infrastructure.models.models.users import Users
from enowshop.infrastructure.models.models.orders import Orders
from enowshop.infrastructure.models.models.products import Products
from enowshop.infrastructure.models.models.order_items import OrderItems
from sqlalchemy import select, insert, func, and_
from sqlalchemy.orm import selectinload, load_only

from enowshop.infrastructure.repositories.repository import SqlRepository
from sqlalchemy import Unicode
from sqlalchemy import select, update
from enowshop.infrastructure.models.models.users_address import UserAddress
from sqlalchemy import desc, asc



class OrdersRepository(SqlRepository):
    model = Orders

    def build_order(self, payload: Dict, uuid: str, meta_data: Dict):
        return {
            'uuid': uuid,   
            'total_amount': int(payload['total_value'] * 100),
            'purchase_amount': int(payload['purchase_amount'] * 100),
            'shipping_amount': int(payload['quote_value'] * 100),
            'installments': payload.get('installments', 1),
            'payment_method': payload['payment_method'],
            'meta_data': meta_data,
            'status': payload.get('status', 'pending'),
            'send_type_id': payload.get('quote_type_id'),
            'payment_date': payload.get('payment_date'),
            'payment_id': payload.get('payment_id'),
            'user_id': payload['user_id'],
            'address_id': payload['address_id'],
        }
    
    async def get_order_by_payment_id(self, payment_id: str) -> Orders:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.payment_id == payment_id))
            return result.scalars().first()
        
    async def get_orders_by_menager(self, params: Dict):
        async with self.session_factory() as session:
            query = select(self.model).limit(params.get('limit')).offset(params.get('offset'))
            total_query = select([func.count(self.model.id)])
            if params.get('start_date') and params.get('end_date'):
                query = query.where(self.model.created_at.between(params.get('start_date'), params.get('end_date')))

            if params.get('send_status'):
                query = query.where(self.model.status_send == params.get('send_status'))
                total_query = total_query.where(self.model.status_send == params.get('send_status'))
            
            total = await session.execute(total_query)
            if params.get('order_type') == 'desc':
                results = await session.execute(query.order_by(desc(params.get('order_by'))))
            else:
                results = await session.execute(query.order_by(asc(params.get('order_by'))))

            total = total.scalar()
            results = results.scalars().all()

            return results, total


    async def get_all_order_with_parans(self, params: Dict):
        async with self.session_factory() as session:
            if params.get('expirate'):
                query = select(self.model)
            else:
                query = select(self.model).limit(params.get('limit')).offset(params.get('offset'))
            if params.get('status'):
                query = query.where(self.model.status == params.get('status'))
            if params.get('expirate'):
                tempo_limite = datetime.now() - timedelta(minutes=15)
                query = query.where(and_(self.model.status == 'pending', self.model.created_at <= tempo_limite))
            
            total = await session.execute(select([func.count(Products.id)]).select_from(Products))
            results = await session.execute(query)

            total = total.scalar()
            results = results.scalars().all()

            return results, total
    
    async def get_order_by_uuid(self, uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .where(self.model.uuid == uuid)
                .options(selectinload(self.model.address))
                .options(selectinload(self.model.order_items).selectinload(OrderItems.product))
            )
            return result.scalars().first()
    
    async def filter_by_json_order_mp_id(self, id):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.meta_data['payment']['id'].astext == id))
            return result.scalars().first()

    async def update_order_by_uuid(self, uuid: str, values: Dict):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.uuid == uuid).values(**values))
            await session.commit()
    
    async def update_order_by_payment_id(self, uuid: str, values: Dict):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.uuid == uuid).values(**values))
            await session.commit()
    
    async def get_orders_by_user(self, user_id: str, params: Dict):
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.user_id == user_id).options(selectinload(self.model.order_items)
                    .selectinload(OrderItems.product)).limit(params.get('limit')).offset(params.get('offset'))
            total = await session.execute(select([func.count(self.model.id)]))
            results = await session.execute(query.order_by(self.model.created_at.desc()))

            total = total.scalar()
            results = results.scalars().all()

            return results, total
        
    async def get_orders_between_dates(self, start_date: datetime, end_date: datetime):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.created_at.between(start_date, end_date)).where(self.model.status == 'approved'))
            return result.scalars().all()
        
    async def get_order_does_not_concluded_or_cancel(self, start_date: datetime, end_date: datetime):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.status != 'approved').where(self.model.created_at.between(start_date, end_date)))
            return result.scalars().all()
        
    async def get_order_group_by_state(self, start_date: datetime, end_date: datetime):
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    UserAddress.state,
                    func.count().label('total')
                ).select_from(
                    self.model
                ).join(
                    UserAddress, self.model.address_id == UserAddress.id
                ).where(
                    self.model.created_at.between(start_date, end_date)
                ).group_by(
                    UserAddress.state
                )
            )
            results = result.all()
            orders_summary = [(state.value, total) for state, total in results]
            orders = dict(orders_summary)

            return orders

    async def get_order_group_by_payment_method(self, start_date: datetime, end_date: datetime):
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    Orders.payment_method,
                    func.count().label('total')
                ).where(
                    Orders.created_at.between(start_date, end_date)
                ).group_by(
                    Orders.payment_method
                )
            )
            results = result.all()
            orders_summary = [(payment_method, total) for payment_method, total in results]
            orders = dict(orders_summary)
            return orders

        


class OrderItemsRepository(SqlRepository):
    model = OrderItems

    async def create_order_items(self, order_items: List[Dict]):
        async with self.session_factory() as session:
            items = [self.model(**order_item) for order_item in order_items]
            model = session.add_all(items)
            await session.commit()
            return model
    
    async def update_by_product_id(self, pk, values):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.product_id == pk).values(**values))
            await session.commit()
    
    async def get_order_items_by_order_id(self, order_id: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.order_id == order_id))
            return result.scalars().all()
    
    async def get_product_by_order_id(self, order_id: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model, Products)
                                           .join(Products, self.model.product_id == Products.id)
                                           .where(self.model.order_id == order_id))
            products = []
            for row in result:
                products.append({
                    'name': row.Products.name,
                    'quantity': row.OrderItems.quantity,
                    'image': row.Products.image_url,
                    'price': row.OrderItems.unity_price,
                })
            return products
    
    async def get_top_3_products_most_sold(self, start_date: datetime, end_date: datetime):
        async with self.session_factory() as session:
            result = await session.execute(
                select(
                    Products.name,
                    func.sum(OrderItems.quantity).label('total')
                ).select_from(
                    OrderItems
                ).where(
                    self.model.created_at.between(start_date, end_date)
                ).join(
                    Products, OrderItems.product_id == Products.id
                ).group_by(
                    Products.name
                ).order_by(
                    'total'
                ).limit(3)
            )
            results = result.all()
            results.reverse()
            products_summary = [(name, total) for name, total in results]
            products = dict(products_summary)
            return products


class ProductsRepository(SqlRepository):
    model = Products

    async def get_products_by_list_uuid(self, uuids: List[str]) -> List[Products]:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model)
                                           .where(self.model.id.in_(uuids))
                                           .options(selectinload(Products.stocks)))
            return result.scalars().all()
    
    async def get_products_by_uuid(self, uuid: str) -> Products:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.sku == uuid))
            return result.scalars().first()
    
    async def get_products_by_id(self, id: str) -> Products:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.id == id))
            return result.scalars().first()

class UserRepository(SqlRepository):
    model = Users
