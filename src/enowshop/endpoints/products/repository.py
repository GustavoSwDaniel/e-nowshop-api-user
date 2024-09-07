from typing import Dict, List, Tuple, Any

from enowshop.infrastructure.models.models.category import Category
from enowshop.infrastructure.models.models.category_products import CategoryProducts
from enowshop.infrastructure.models.models.promotion import Promotion

from enowshop.infrastructure.models.models.products import Products
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload, load_only

from enowshop.endpoints.paginate import paginate
from enowshop.infrastructure.repositories.repository import SqlRepository


class ProductsRepository(SqlRepository):
    model = Products

    async def get_all_products_with_category(self, params: Dict, products_id: List = None):
        async with self.session_factory() as session:
            query = select(Products).limit(params.get('limit')).offset(params.get('offset'))
            if products_id:
                query = query.where(Products.id.in_(products_id))
            if params.get('min_price'):
                query = query.where(Products.price >= params.get('min_price'))
            if params.get('name'):
                query = query.where(Products.name.ilike(f'%{params.get("name")}%'))
            if params.get('order_by') == 'created_at':
                if params.get('order') == 'asc':
                    query = query.order_by(Products.created_at.asc())
                else:
                    query = query.order_by(Products.created_at.desc())
            if params.get('order_by') == 'price':
                if params.get('order') == 'asc':
                    query = query.order_by(Products.price.asc())
                else:
                    query = query.order_by(Products.price.desc())
            if params.get('order_by') == 'market':
                query = query.order_by(Products.market.desc())

            if not params.get('all'):
                query = query.where(Products.is_active == True)

            if products_id:
                total = await session.execute(select([func.count(Products.id)]).where(Products.id.in_(products_id)).select_from(Products))
            else:
                total = await session.execute(select([func.count(Products.id)]).select_from(Products))

            query = query.options(selectinload(Products.stocks))
            results = await session.execute(query.options(
                selectinload(Products.category_products).options(selectinload(CategoryProducts.category))))

            total = total.scalar()
            results = results.scalars().all()

            for result in results:
                setattr(result, 'category',
                        [category_products.category for category_products in result.category_products])

        return results, total

    async def get_product_by_promotion_uuid(self, promotion_uuid: str, params) -> Tuple[Any, Any]:
        async with self.session_factory() as session:
            total = await session.execute(select([func.count(self.model.id)])
                                          .join(Promotion, Promotion.id == self.model.promotion_id)
                                          .where(Promotion.uuid == promotion_uuid)
                                          .select_from(Products))

            result = await session.execute(select(self.model).limit(params.get('limit')).offset(params.get('offset'))
                                           .join(Promotion, Promotion.id == self.model.promotion_id)
                                           .where(Promotion.uuid == promotion_uuid)
                                           .options(selectinload(Products.category_products).selectinload(CategoryProducts.category))
                                           .options(selectinload(Products.promotion))
                                           )

            total = total.scalar()
            results = result.scalars().all()

            for result in results:
                setattr(result, 'category',
                        [category_products.category for category_products in result.category_products])

            return results, total
    
    async def get_product_with_category(self, params: Dict):
        async with self.session_factory() as session:
            result = await session.execute(
                select(Products)
                .filter_by(**params)
                .options(
                    selectinload(Products.category_products).selectinload(CategoryProducts.category),
                    selectinload(Products.stocks)
                )
            )
            result = result.scalars().first()

            setattr(result, 'category', [category_products.category for category_products in result.category_products])
            return result


    async def get_product_with_category_and_stock(self, params: Dict):
        async with self.session_factory() as session:
            result = await session.execute(
                select(Products).filter_by(**params).options(selectinload(Products.category_products)
                                                             .selectinload(CategoryProducts.category))
                                                             .options(selectinload(Products.stocks)))
            result = result.scalars().first()

            setattr(result, 'category', [category_products.category for category_products in result.category_products])
            return result

    async def get_products_by_list_id_with_category(self, ids: List[str]) -> List[Products]:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.id.in_(ids)).options(selectinload(Products.stocks)))

            return result.scalars().all()

    async def update_by_uuid(self, pk, values):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.sku == pk).values(**values))
            await session.commit()
    
    async def soft_delete_by_uuid(self, pk):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.sku == pk).values(is_active=False))
            await session.commit()
    
    async def reactivate_by_uuid(self, pk):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.sku == pk).values(is_active=True))
            await session.commit()


    async def get_products_by_list_uuid(self, uuids: List[str]) -> List[Products]:
        async with self.session_factory() as session:
            print(uuids)
            result = await session.execute(select(self.model).where(self.model.sku.in_(uuids)).options(selectinload(Products.stocks)))
            return result.scalars().all()
        
    async def get_products_by_list_id(self, ids: List[str]) -> List[Products]:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.id.in_(ids)).options(selectinload(Products.stocks)))
            return result.scalars().all()
        
    async def get_products_by_id_uuid(self, uuids: List[str]) -> List[Products]:
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


class CategoryProductsRepository(SqlRepository):
    model = CategoryProducts

    async def get_all_products_id_by_category(self, category_id: int) -> List[int]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model.product_id).where(self.model.category_id == category_id)
            )

            return result.scalars().all()


class CategoryRepository(SqlRepository):
    model = Category
