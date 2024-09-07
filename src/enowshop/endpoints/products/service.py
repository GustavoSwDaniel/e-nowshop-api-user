from typing import Dict
import uuid
import random
from enowshop.endpoints.helpers import float_to_int
from enowshop.endpoints.paginate import paginate
from enowshop.endpoints.products.repository import ProductsRepository, CategoryProductsRepository, CategoryRepository
from enowshop.endpoints.promotions.repository import PromotionsRepository
from enowshop.endpoints.stock.repository import StockRepository


class ProductsService:
    def __init__(self, products_repository: ProductsRepository, category_repository: CategoryRepository,
                 category_products_repository: CategoryProductsRepository, stock_repository: StockRepository,
                 promotion_products: PromotionsRepository):
        self.products_repo = products_repository
        self.category_repo = category_repository
        self.category_products = category_products_repository
        self.promotion_products = promotion_products
        self.stock_repository = stock_repository

    async def register_product(self, product: dict):
        category = await self.category_repo.filter_by({'uuid': product.pop('category_uuid')})
        product = await self.products_repo.create(product)
        await self.category_products.create({'category_id': category.id, 'product_id': product.id})

        stock = await self.stock_repository.filter_by({'product_id': product.id})
        if not stock:
            await self.products_repo.update_by_uuid(pk=product.sku, values={'is_active': False})

        return product

    async def get_all_products(self):
        return await self.products_repo.get_all()

    async def get_product_by_uuid(self, product_uuid: str, params: Dict):
        if params.get('stock'):
            results =  await self.products_repo.get_product_with_category_and_stock({'sku': product_uuid})
            if results.stocks:
                setattr(results, 'price', results.stocks[0].price / 100)
                for stock in results.stocks:
                    setattr(stock, 'price', stock.price / 100)
        else:
            results =  await self.products_repo.get_product_with_category({'sku': product_uuid})
            response = await self.stock_repository.filter_all_by({'product_id': results.id})
            if params.get('recomendation'):
                if results.recomendations:
                    if len(results.recomendations.keys()) > 0:
                        recomendations_ids = dict(sorted(results.recomendations.items(), key=lambda x:x[1], reverse=True)).keys()
                        recomendations = await self.products_repo.get_products_by_list_id_with_category([int(key) for key in recomendations_ids])
                else:
                    product_ids = []
                    if len(results.category_products) > 6:
                        while len(product_ids < 6):
                            product_choiced = random.choice(results.category_products)
                            if product_choiced.product_id not in product_ids:
                                product_ids.append(product_choiced.product_id)
                        recomendations = await self.products_repo.get_products_by_list_id_with_category(product_ids)
                    else:
                        recomendations = await self.products_repo.get_products_by_list_id_with_category([i.product_id for i in results.category_products if i.product_id != results.id])
                        
                setattr(results, 'recomendations_products', recomendations)

            setattr(results, 'price', response[0].price / 100)
        return results

    async def get_all_products_with_category(self, params: Dict):
        products_id = []
        if params.get('category'):
            category = await self.category_repo.filter_by({'uuid': params.pop('category')})
            products_id = await self.category_products.get_all_products_id_by_category(category_id=category.id)

        results, total = await self.products_repo.get_all_products_with_category(params=params, products_id=products_id)
        for result in results:
            response = await self.stock_repository.filter_all_by({'product_id': result.id})

            if not response:
                continue
            setattr(result, 'price', response[0].price / 100)
            
        return paginate(results, params.get('offset'), total)

    async def update_product_by_uuid(self, product_id, product):
        product_data = await self.products_repo.filter_by({'sku': product_id})
        if product.get('category'):
            category = await self.category_repo.filter_by({'uuid': product['category']})
            del product['category']
            category_products = await self.category_products.filter_by({'product_id': product_data.id})
            if not category_products:
                await self.category_products.create({'category_id': category.id, 'product_id': product_data.id})
            else:
                await self.category_products.update(category_products.id, {'category_id': category.id})
        await self.products_repo.update_by_uuid(pk=product_id, values=product)

    async def change_status_active(self, product_uuid, action):
        actions = {
            'activate': self.products_repo.reactivate_by_uuid,
            'deactivate': self.products_repo.soft_delete_by_uuid
        }
        await actions[action](product_uuid)

    @staticmethod
    def calc_new_price(results):
        for result in results:
            setattr(result, 'new_price', result.price - (result.price * (result.promotion.discount / 100)))
        return results

    async def get_products_by_promotion(self, promotion_uuid, params: Dict):
        results, total = await self.products_repo.get_product_by_promotion_uuid(promotion_uuid=promotion_uuid,
                                                                                params=params)
        results = self.calc_new_price(results)
        return paginate(results, params.get('offset'), total)