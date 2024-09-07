# create a serivice file to handle the business logic


# Path: src/enowshop/endpoints/stock/service.py

import random
import string
from typing import List, Dict, Any, Tuple

from enowshop.endpoints.stock.repository import StockRepository
from enowshop.infrastructure.models.models.stock import Stock
from enowshop.endpoints.products.repository import ProductsRepository
from enowshop.endpoints.paginate import paginate

class StockService:
    def __init__(self, stock_repository: StockRepository, product_repository: ProductsRepository):
        self.stock_repository = stock_repository
        self.product_repository = product_repository

    def generate_sku(self, product_name):
        product_name = product_name.strip().lower()
        product_name = ''.join(char for char in product_name if char.isalnum())
        
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        sku = product_name[:6] + random_suffix
        
        return sku

    async def register_stock(self, stock: Dict) -> Stock:
        product = await self.product_repository.filter_by({'sku': stock.pop('product_sku')})
        if product.is_active == False:
            await self.product_repository.update_by_uuid(product.sku, {'is_active': True})
        stock['product_id'] = product.id
        stock = await self.stock_repository.create(stock)
        return stock

    async def get_all_stock(self, params: Dict) -> Tuple[List[Stock], int]:
        result, total =  await self.stock_repository.get_all_stock(params)
        return paginate(result, params.get('offset'), total)

    async def get_stock_by_uuid(self, stock_uuid: str) -> Stock:
        return await self.stock_repository.filter_by({'uuid': stock_uuid})

    async def update_stock(self, stock_uuid: str, stock: Dict) -> Stock:
        return await self.stock_repository.update_by_uuid(stock_uuid, stock)

    async def delete_stock(self, stock_uuid: str) -> None:
        return await self.stock_repository.soft_delete_by_uuid(stock_uuid)