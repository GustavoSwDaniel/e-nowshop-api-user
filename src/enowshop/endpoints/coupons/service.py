
from datetime import datetime, date
from random import choice
from enowshop.endpoints.coupons.repository import CouponsProductsRepository, CouponsRepository
from enowshop.endpoints.products.repository import ProductsRepository


class CouponService:
    def __init__(self, coupon_repository: CouponsRepository, 
                 coupon_product_repository: CouponsProductsRepository,
                 product_repository: ProductsRepository) -> None:
        self.coupon_repository = coupon_repository
        self.coupon_product_repository = coupon_product_repository
        self.product_repository = product_repository

    async def generate_random_coupon(self):
        while True:
            coupon = ''.join([choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(6)])
            if not await self.coupon_repository.check_coupon_exists(coupon):
                break
        return {"code": coupon}
    
    async def create_coupon(self, coupon_data):
        if await self.coupon_repository.check_coupon_exists(coupon_data['code']):
            raise ValueError("Coupon already exists")
        
        producs = await self.product_repository.get_products_by_list_uuid(coupon_data.pop('products'))
        products_ids = [product.id for product in producs]
        coupon_data['code'] = coupon_data['code'].upper()
        coupon_data['expiration_date'] = datetime.strptime(coupon_data['expiration_date'], "%Y-%m-%d")
        coupon = await self.coupon_repository.create(coupon_data)
        await self.coupon_product_repository.bulk_create([{"coupon_id": coupon.id, "product_id": product_id} for product_id in products_ids])
        return coupon

    async def deactivate_coupon(self, coupon_id):
        coupon = await self.coupon_repository.filter_by({'id': coupon_id})
        await self.coupon_repository.update(pk=coupon.id, values={"is_active": False, "expiration_date": date.today()})
        return coupon
    
    async def get_coupons(self):
        return await self.coupon_repository.get_all()
    
