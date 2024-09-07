import base64
import datetime
import io
import json
from typing import Dict, List
from uuid import uuid4



from enowshop.endpoints.paginate import paginate
from enowshop.endpoints.quotes.service import QuotesService
from enowshop.endpoints.cars.service import CarsService
from decimal import Decimal
import pyqrcode

from enowshop.endpoints.orders.repository import OrdersRepository, ProductsRepository, OrderItemsRepository
from enowshop.endpoints.quotes.repository import UsersAddressRepository
from enowshop.domain.Asaas.asaas_client import AsaasClient
from enowshop.infrastructure.models.models.users import Users
from enowshop.endpoints.users.repository import UsersRepository
from enowshop.endpoints.stock.repository import StockRepository

from enowshop.endpoints.financers.repository import FinancersRepository
from enowshop.domain.melhor_envio.melhor_envio import MelhorEnvio

class OrdersService:
    def __init__(self, orders_repository: OrdersRepository, products_repository: ProductsRepository,
                 order_items_repository: OrderItemsRepository, user_reponsitory: UsersRepository,
                 user_address_repository: UsersAddressRepository, payment_access_token: Dict,
                 car_service: CarsService, asaas_client: AsaasClient, stock_repository: StockRepository,
                 financers_repository: FinancersRepository, melhor_envio: MelhorEnvio):
        self.orders_repository = orders_repository
        self.products_repository = products_repository
        self.order_items_repository = order_items_repository
        self.user_reponsitory = user_reponsitory
        self.user_address_repository = user_address_repository
        self.payment_access_token = payment_access_token
        self.car_service = car_service
        self.asaas_client = asaas_client
        self.stock_repository = stock_repository
        self.financers_repository = financers_repository
        self.melhor_envio = melhor_envio

    @staticmethod
    def __build_order_items(products: List[Dict], order_id: int) -> List[Dict]:
        order_items = []
        for product in products:
            order_items.append({'product_id': product['product_id'], 'quantity': product['quantity'],'order_id': order_id, 'unity_price': product['price'], 'total_price': product['price'] * product['quantity']})

        return order_items

    @staticmethod
    def __pix_payment(self, value: int):
        qrcode_data = {'type': 'pix', 'value': {value}}
        code = pyqrcode.create(str(qrcode_data))
        file = io.BytesIO()
        code.png(file, scale=6)
        encoded = base64.b64encode(file.getvalue()).decode("ascii")
        return {
            'value': value,
            'base64': 'data:image/png;base64,' + encoded,
            'expiration_date': datetime.datetime.now()
        }
    
    async def sum_products(self, products: List[Dict]) -> float:
        total = 0
        for product in products:
            product_data = await self.products_repository.get_products_by_uuid(uuid=product['uuid'])
            total += (product_data.price / 100) * product['quantity']

        return total

    async def build_pix_payload(self, products: List, quote_value: float):
        return {
            'total_value': 1,
            'user_info': { # round(Decimal(payload_payment.get("total_value")), 2)
                'email': 'gustavodanieldetoledo@gmail.com',
                'first_name': 'gustavo',
                'last_name': 'daniel'
            }
        }
    
    async def get_user_data(self, uuid: str) -> Users:
        return await self.user_reponsitory.get_user_with_phone(uuid=uuid)

    def build_payload_topic(self, payment_id: str, order_uuid: str) -> Dict:
        return {
            'payment_id': payment_id,
            'order_uuid': order_uuid
        }
    
    def transform_payment_type(self, payment_type: str) -> str:
        return {
            'card': 'credit_card',
            'pix': 'pix',
            'billet': 'boleto'
        }.get(payment_type)


    async def create_order(self, order_data: Dict, user_uuid_keycloak: str) -> Dict:
        try:
            products_data = order_data.pop('items')
            order_uuid = str(uuid4())
            
            user_data = await self.get_user_data(uuid=user_uuid_keycloak)
            order_data['user_id'] = user_data.id
            user_asaas = {}
            if not user_data.user_asaas:
                user_asaas = await self.asaas_client.create_customer({
                    'name': user_data.name,
                    'cpf': user_data.cpf,
                    'phone': user_data.user_phones[0].number
                })
                await self.user_reponsitory.update(pk=user_data.id, values={'user_asaas': user_asaas['id']})
                order_data['customer'] = user_asaas['id']
            else:
                order_data['customer'] = user_data.user_asaas 
            if order_data['payment_method'] == 'card':
                
                order_data['card_holder_info'] = {
                    'name': user_data.name,
                    'email': user_data.email,
                    'cpf': user_data.cpf,
                    'cep': user_data.user_address[0].cep,
                    'number': user_data.user_address[0].number,
                    'phone': user_data.user_phones[0].number
                }

            payment_info = await self.asaas_client.create_order(order_data=order_data)
            if order_data['payment_method'] == 'card' and 'errors' in payment_info.keys():
                raise Exception("Error")
            if payment_info.get('status') and payment_info.get('status') == 'CONFIRMED':
                order_data['status'] = 'approved'
            
            order_data['payment_id'] = payment_info['id']
            order_data['payment_method'] = self.transform_payment_type(order_data['payment_method'])
            order_builded = self.orders_repository.build_order(payload=order_data,
                                                                    uuid=order_uuid, meta_data={
                                                                        'payment': payment_info})
            order = await self.orders_repository.create(order_builded)

            products_uuid = [product_uuid['uuid'] for product_uuid in products_data]
            products = await self.products_repository.get_products_by_list_uuid(uuids=products_uuid)
            products_id = []
            products_send = []
            for product_data in products_data:
                for product in products:
                    if product_data['uuid'] == product.sku:
                        stock = await self.stock_repository.get_stock_by_produc_id(product_id=product.id)
                        products_id.append({'product_id': product.id, 'quantity': product_data['quantity'], 'price': stock[0].price / 100})
                        products_send.append({'product_id': product.id, 'quantity': product_data['quantity'], 
                                              'name': product.name,
                                              'physical_characteristics': product.physical_characteristics})

            order_items = self.__build_order_items(products=products_id, order_id=order.id)

            await self.order_items_repository.create_order_items(order_items=order_items)
            # for product in products_id:
            #     stock = await self.stock_repository.get_stock_by_produc_id(product_id=product['product_id'])
            #     await self.stock_repository.update(pk=stock[0].id, values={'quantity': stock[0].quantity - product['quantity']})
            #     for product_send in products_send:
            #         if product['product_id'] == product_send['product_id']:
            #             product_send['price'] = stock[0].price / 100

            
            await self.car_service.empty_car(user_uuid=user_uuid_keycloak)

            if order_data['payment_method'] == 'credit_card' and payment_info.get('status') == 'CONFIRMED':
                for product in products_id:
                    stock = await self.stock_repository.get_stock_by_produc_id(product_id=product['product_id'])
                    await self.stock_repository.update(pk=stock[0].id, values={'quantity': stock[0].quantity - product['quantity']})
                    for product_send in products_send:
                        if product['product_id'] == product_send['product_id']:
                            product_send['price'] = stock[0].price / 100

                await self.financers_repository.create({
                    "name": f"Carto-de-credito-venda-{order_uuid}",
                    "is_recurrent": False,
                    "type": "venda",
                    'value': payment_info.get('netValue'),
                })

                payment_send = self.melhor_envio.build_payload(data=user_data, order_data=order_data, products=products_send)
                send_order = await self.melhor_envio.generate_labels(payment_send)
                await self.orders_repository.update_order_by_uuid(uuid=order_uuid, values={'send_infos': {'order_melhor_envio': send_order}})

            if payment_info.get('payload'):
                payment_info.pop('payload')
            return {
                "uuid": order_uuid,
                "payment_info": payment_info
            }
        except Exception as e:
            return {
                'uuid': order_uuid,
                'payment_info': {
                    'billingType': 'error', 
                    'value': 0,
                    'status': 'error',
                    'message': str(e)
                }
            }
    async def get_order_by_uuid(self, order_uuid: str):
        return await self.orders_repository.get_order_by_uuid(uuid=order_uuid)

    async def get_all_orders(self, params: Dict) -> List:
        results, total =  await self.orders_repository.get_all_order_with_parans(params=params)
        return paginate(results, params.get('offset'), total)

    async def update_order_status(self, order_uuid: str, status: str) -> None:
        await self.orders_repository.update_order_by_uuid(uuid=order_uuid, values={'status': status})
    
    async def update_order_status_send(self, order_uuid: str, status_send: str) -> None:
        await self.orders_repository.update_order_by_uuid(uuid=order_uuid, values={'status_send': status_send})

    async def decrement_products_quantity(self, order_id: str) -> None:
        order = await self.orders_repository.get_order_by_uuid(uuid=order_id)
        products = await self.order_items_repository.get_order_items_by_order_id(order_id=order.id)
        for product in products:
            product_data = await self.products_repository.get_products_by_id(product.product_id)
            await self.products_repository.update(pk=product.product_id, values={'unity': product_data.unity - product.quantity, 'market': product_data.market + product.quantity})
        return
        
    async def get_orders_by_user(self, user_uuid: str, params: Dict) -> List:
        user = await self.user_reponsitory.filter_by({'uuid': user_uuid})
        results, total = await self.orders_repository.get_orders_by_user(user_id=user.id, params=params)
        return paginate(results, params.get('offset'), total)

    async def get_products_by_order_id(self, order_uuid: str) -> List:
        order = await self.orders_repository.filter_by({'uuid': order_uuid})
        products = await self.order_items_repository.get_product_by_order_id(order_id=order.id)
        return products
    
    def transalate_status(self, status: str) -> str:
        status_dict = {
            'RECEIVED': 'approved',
        }
        return status_dict.get(status)

    async def check_and_update_orders(self, data: Dict) -> None:
        order = await self.orders_repository.get_order_by_payment_id(payment_id=data['payment']['id'])
        if order and order.status != 'approved':
            if data.get('billingType') != 'credit_card':
                await self.financers_repository.create({
                        "name": f"{data.get('payment')['billingType']}-venda-{order.uuid}",
                        "is_recurrent": False,
                        "type": "venda",
                        'value': data.get('payment')['netValue'],
                    })
            
                user_data = await self.user_reponsitory.get_user_by_id(user_id=order.user_id)
            
                order_dict = order.__dict__

                order_products = await self.order_items_repository.get_order_items_by_order_id(order_id=order.id)

                products_list = await self.products_repository.get_products_by_list_id(ids=[product.product_id for product in order_products])

                products_send = []
                for product in products_list:
                    for order_product in order_products:
                        if product.id == order_product.product_id:
                            stock = await self.stock_repository.get_stock_by_produc_id(product_id=product.id)
                            products_send.append({'product_id': product.id, 'quantity': order_product.quantity, 
                                                'name': product.name,
                                                'physical_characteristics': product.physical_characteristics,
                                                'price': stock[0].price / 100})
                                                
                payment_send = self.melhor_envio.build_payload(data=user_data, order_data=order_dict, products=products_send)
                send_order = await self.melhor_envio.generate_labels(payment_send)
                await self.orders_repository.update_order_by_uuid(uuid=order.uuid, values={'status': self.transalate_status(data['payment']['status']), 
                                                                                        'payment_date': datetime.datetime.strptime(data['payment']['paymentDate'], '%Y-%m-%d'), 
                                                                                        'send_infos': {'order_melhor_envio': send_order}})
                
    async def get_orders_by_menager(self, params: Dict):
        if params.get('start_date'):
            params['start_date'] = datetime.datetime.strptime(params['start_date'], '%Y-%m-%d')
        if params.get('end_date'):
            params['end_date'] = datetime.datetime.strptime(params['end_date'], '%Y-%m-%d')

        results, total = await self.orders_repository.get_orders_by_menager(params=params)
        return paginate(results, params.get('offset'), total)

    async def get_labels(self, order_uuid: str):
        order = await self.orders_repository.get_order_by_uuid(uuid=order_uuid)
        if not order.send_infos.get('order_melhor_envio'):
            return {'error': 'Order not send'}
        labels = await self.melhor_envio.get_labels(orders=order.send_infos['order_melhor_envio'])
        await self.orders_repository.update_order_by_uuid(uuid=order_uuid, values={'link_label_print': labels})
        return labels
    