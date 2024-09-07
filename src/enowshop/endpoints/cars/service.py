from typing import Dict, List

from enowshop.infrastructure.models.models.users import Users

from enowshop.endpoints.orders.repository import ProductsRepository

from enowshop.domain.noql_models import Cars, Items
from enowshop.endpoints.cars.repository import CarsRepository, UserRepository, CartItensRepository
from enowshop.endpoints.quotes.service import QuotesService
from datetime import date

from enowshop.domain.melhor_envio.melhor_envio import MelhorEnvio
from enowshop.endpoints.coupons.repository import CouponsProductsRepository, CouponsRepository


class CarsService:
    def __init__(self, cars_repository: CarsRepository,
                 products_repository: ProductsRepository,
                 user_repository: UserRepository,
                 car_items_repository: CartItensRepository,
                 cupom_repository: CouponsRepository,
                 cupom_products_repository: CouponsProductsRepository,
                 melhor_envio: MelhorEnvio) -> None:
        self._cars_repository = cars_repository
        self._products_repository = products_repository
        self._users_repository = user_repository
        self._car_items_repository = car_items_repository
        self._melhor_envio = melhor_envio
        self._cupom_repository = cupom_repository
        self._cupom_products_repository = cupom_products_repository
        

    async def create_cars(self, uuid: str):
        car = Cars(user_uuid=uuid, items=[])
        await self._cars_repository.create(car)

    async def get_user_by_keycloak_uuid(self, user_uuid: str) -> Users:
        return await self._users_repository.filter_by_with_address(user_keycloack_uuid=user_uuid)

    def _build_payload_to_calc_quotes(self, products: Dict, destination_post_code) -> List:
        products_cal = {'products': []}
        for product in products:
            products_cal['products'].append({
                "id": product.id,
                "width": product.width,
                "height": product.height,
                "length": product.length,
                "weight": product.weight,
                "quantity": product.quantity_car,
            })

        payload = {
            'from': {
                'postal_code': self._melhor_envio.origin_cep
            },
            'to': {
                'postal_code': destination_post_code
            },
            'products': products_cal['products']
        }
        return payload

    def define_type_send(self, type_send: str) -> int:
        type_send_dict = {
            'SEDEX': 0,
            'PAC': 1,
            'TRANSPORTADORA': 2
        }
        print(type_send)
        return type_send_dict[type_send]
    
    async def calcs_quotes(self, products: Dict, user_address) -> Dict:

        payload = self._build_payload_to_calc_quotes(products, user_address[0].cep)
        quotes_data = await self._melhor_envio.calc_quotes(payload=payload)

        quotes = []

        for quote in quotes_data:
            if 'error' not in quote.keys():
                quotes.append({
                    'id': quote['id'],
                    'name': quote['name'],
                    'price': quote['price'],
                    'delivery_time': quote['delivery_time'],
                })

        return quotes
        

    async def get_select_quotes(self, quotes: Dict, send_type: str) -> tuple:
        type_send = self.define_type_send(send_type)
        quoet_valeu = quotes[type_send]
        quoet_valeu = float(quoet_valeu.get('valor', '0,0').replace(',', '.'))
        return quoet_valeu

    async def get_car_with_user_uuid(self, user_uuid: str, send_type: str = None, destination_post_code: str = None, cupom: str = None) -> Dict:        
        user = await self._users_repository.filter_by_with_address({'uuid':user_uuid})
        eligible_products = []
        cupom_data = None

        if cupom:
            cupom_data = await self._cupom_repository.filter_by({'code': cupom})
            if cupom_data and cupom_data.expiration_date > date.today() and cupom_data.is_active:
                cupom_products = await self._cupom_products_repository.filter_all_by({'coupon_id': cupom_data.id})
                for product in cupom_products:
                    eligible_products.append(product.product_id)
            else:
                return {'error': 'Cupom invalido'}


        cart_porducts = await self._cars_repository.get_cart(user_id=user.id)
        if not cart_porducts:
            products_uuid = []
            products = []
        else:
            products_uuid = [item.product_id for item in cart_porducts.cart_items]
            products = await self._products_repository.get_products_by_id_uuid(products_uuid)
        total  = 0
        offer = 0
        previous_stock = None
        for product in products:
            for item in cart_porducts.cart_items:
                if product.id == item.product_id:
                    if not product.stocks:
                        return {'error': 'Product out of stock'}
                    if len(product.stocks) > 1:
                        current_stock = product.stocks[-2]
                    else:
                        current_stock = product.stocks[-1]
                    if len(product.stocks) > 1:
                        previous_stock = product.stocks[-1]
                    if previous_stock and (previous_stock.price < current_stock.price):
                        offer += (current_stock.price - previous_stock.price) / 100
                        product_offer = (current_stock.price - previous_stock.price) / 100
                        product_price = previous_stock.price / 100
                        setattr(product, 'width', product.physical_characteristics['Width']) #  largura
                        setattr(product, 'height', product.physical_characteristics['Height']) # altura 
                        setattr(product, 'length', product.physical_characteristics['Length']) # comprimento
                        setattr(product, 'weight', product.physical_characteristics['Weight']) # peso
                        setattr(product, 'price', f'{product_price:.2f}')
                        if cupom_data:
                            if product.id in eligible_products:
                                offer = product_price * (cupom_data.total_sold / 100)
                                setattr(product, 'offer', f'{product_price * (cupom_data.total_sold / 100):.2f}')
                        else:
                            setattr(product, 'offer', f'{product_offer:.2f}')
                    else:
                        product_price = current_stock.price / 100
                        setattr(product, 'width', product.physical_characteristics['Width'])
                        setattr(product, 'height', product.physical_characteristics['Height'])
                        setattr(product, 'length', product.physical_characteristics['Length'])
                        setattr(product, 'weight', product.physical_characteristics['Weight'])
                        setattr(product, 'price', f'{product_price:.2f}')
                        if cupom_data:
                            if product.id in eligible_products:
                                setattr(product, 'offer', f'{product_price * (cupom_data.total_sold / 100):.2f}')
                    setattr(product, 'quantity_car', item.quantity)

        cupom_offer = 0
        total_without_offer = 0
        for product in products:
            if product.__dict__.get('offer'):
                total = total + (product.quantity_car * (float(product.price) - float(product.offer)))
                total_without_offer = total_without_offer + (product.quantity_car * (float(product.price)))
                cupom_offer += product.quantity_car * float(product.offer)
            else:
                total = total + (product.quantity_car * float(product.price))
                total_without_offer=total

        values =  {
            'user_uuid': user_uuid,
            'items': products,
            'cart_total': f'{total:.2f}',
            'total_without_offer': f'{total_without_offer:.2f}',
            'cart_total_term': f'{total:.2f}',
            'cash': f'{total:.2f}',
            'offer': f'{cupom_offer:.2f}'
        }


        if cupom_offer > 0:
            values['cupom_offer'] = f'{cupom_offer:.2f}'

        quotes = None
        if destination_post_code or user.user_address:
            quotes = await self.calcs_quotes(products=products, user_address=user.user_address)
            values['quoets'] = quotes

        if send_type:
            quoet_valeu = list(filter(lambda quote: quote['id'] == int(send_type), quotes))
            total += float(quoet_valeu[0]['price'])
            values['cart_total_term'] = f'{total:.2f}'
            values['cash'] = f'{total:.2f}'
            values['quoet_value'] = quoet_valeu[0]['price']
            values['chosen_quote'] = quoet_valeu[0]['name']

        if not products:
            values['quoets'] = []
            
        return values

    async def add_item_in_car(self, data, user_uuid: str):
        data['quantity'] = 1
        product = await self._products_repository.get_products_by_uuid(uuid=data.pop('product_uuid'))
        user = await self._users_repository.filter_by({'uuid':user_uuid})
        data['product_id'] = product.id
        cart = await self._cars_repository.filter_by({'user_id': user.id, 'expired': False})
        if not cart:
            cart = await self._cars_repository.create({'user_id': user.id})
        cart_items = await self._car_items_repository.filter_by({'cart_id': cart.id, 'product_id': product.id})
        if cart_items:
            await self._car_items_repository.change_quantity_item_in_car(item_uuid=product.id, cart_id=cart.id,
                                                                new_quantity=cart_items.quantity + 1)
            return

        car = await self._car_items_repository.create({
            'cart_id': cart.id, 'product_id': product.id, 'quantity': 1
        })
        return
        

    async def remove_item_in_car(self, item_uuid: str, user_uuid: str):
        user = await self._users_repository.filter_by({'uuid':user_uuid})
        cart = await self._cars_repository.get_cart(user_id=user.id)
        product = await self._products_repository.get_products_by_uuid(uuid=item_uuid)
        await self._car_items_repository.remove_item_from_car(item_uuid=product.id, 
                                                              cart_id=cart.id)

    async def change_quantity_item_in_car(self, item_uuid: str, user_uuid: str, new_quantity: int):
        user = await self._users_repository.filter_by({'uuid':user_uuid})
        cart = await self._cars_repository.filter_by({'user_id': user.id, 'expired': False})
        product = await self._products_repository.get_products_by_uuid(uuid=item_uuid)
        await self._car_items_repository.change_quantity_item_in_car(item_uuid=product.id, cart_id=cart.id,
                                                                new_quantity=new_quantity)
    
    async def empty_car(self, user_uuid: str):
        user = await self._users_repository.filter_by({'uuid':user_uuid})
        cart = await self._cars_repository.get_cart(user_id=user.id)
        if not cart:
            return
        items = await self._car_items_repository.get_cart_items_by_cart_id(cart.id)
        await self._cars_repository.expirate_cart(pk=cart.id)
        

    async def get_car_lenght(self, user_uuid: str) -> int:
        user = await self._users_repository.filter_by({'uuid':user_uuid})
        car = await self._cars_repository.get_car_by_user_id(user_id=user.id)
        if not car:
            return 0
        car_items = await self._car_items_repository.get_cart_items_by_cart_id(cart_id=car.id)
        return len(car_items)