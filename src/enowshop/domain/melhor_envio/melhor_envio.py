from typing import Dict, List
from httpx import AsyncClient
import copy


class MelhorEnvio:
    def __init__(self, token: str, origin_cep: str) -> None:
        self._token = token
        self.origin_cep = origin_cep
        self.url = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate"

    async def calc_quotes(self, payload: Dict) -> Dict:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._token}'
        }
        async with AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=headers)
            return response.json()

    def build_payload(self, data, order_data, products):
        payload =  {
            "from": {
                "name": "GUSTAVO DANIEL DE TOLEDO",
                "phone": "12999116951",
                "postal_code": "01310100",
                "address": "Rua Francisco Cândido Ribeiro",
                "number": "166",
                "complement": "166",
                "district": "vila britania",
                "city": "Campos do Jordão",
                "state_abbr": "",
                "document": "88804224053",
                "know_my_cnpj": False,
                "state_register": "",
                "economic_activity_code": ""
            },
            "to": {
                "name": f"{data.name} {data.last_name}",
                "phone": data.user_phones[0].number,
                "postal_code": data.user_address[0].cep,
                "address": data.user_address[0].street,
                "number": data.user_address[0].number,
                "complement": "",
                "district": data.user_address[0].village,
                "city": data.user_address[0].city,
                "state_abbr": data.user_address[0].state.name,
                "document": data.cpf,
                "know_my_cnpj": False,
                "state_register": "",
                "economic_activity_code": "",
                "email": data.email,
                "note": ""
            },
            "options": {
                "non_commercial": True,
                "reverse": False,
                "insurance_value": 1.11,
                "receipt": False,
                "own_hand": False,
                "collect": True,
                "reminder": ""
            },
            "service": order_data.get('quote_type_id', order_data.get('send_type_id')),
            "pudo": False
        }

        if (order_data.get('quote_type_id') in [1,2,3] or order_data.get('send_type_id') in [1,2,3]) and len(products) > 1:
            product_count = len(products)
            labels = []
            for i in range(product_count):
                payload_split = copy.deepcopy(payload)
                payload_split['products'] = [
                    {
                        "name": products[i]['name'],
                        "quantity": products[i]['quantity'],
                        "unitary_value": products[i]['price']
                    }
                ]
                payload_split['volumes'] = [
                    {
                        "id": products[i]['product_id'],
                        "height": products[i]['physical_characteristics']['Height'],
                        "width": products[i]['physical_characteristics']['Width'],
                        "length": products[i]['physical_characteristics']['Length'],
                        "weight": products[i]['physical_characteristics']['Weight'],
                        "qntd": products[i]['quantity']
                    }
                ]
                labels.append(payload_split)
            return labels
                        
        products_items = []
        volumes = []
        for product in products:
            products_items.append(
                {
                    "name": product['name'],
                    "quantity": product['quantity'],
                    "unitary_value": product['price']
                }
            )
            volumes.append(
                {
                    "id": product['product_id'],
                    "height": product['physical_characteristics']['Height'],
                    "width": product['physical_characteristics']['Width'],
                    "length": product['physical_characteristics']['Length'],
                    "weight": product['physical_characteristics']['Weight'],
                    "qntd": product['quantity']
                }
            )
        payload['volumes'] = volumes
        payload['products'] = products_items
        return payload
        

    async def generate_labels(self, payload: Dict):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._token}'
        }
        async with AsyncClient() as client:
            order_list = {
                'orders': []
            }
            if isinstance(payload, List):
                for item in payload:
                    response = await client.post('https://sandbox.melhorenvio.com.br/api/v2/me/cart', json=item,
                                          headers=headers)
                    if response.status_code == 201:
                        order_list['orders'].append(
                            response.json()['id'])
            else:
                response = await client.post('https://sandbox.melhorenvio.com.br/api/v2/me/cart', json=payload,
                                          headers=headers)
                if response.status_code == 201:
                    order_list['orders'].append(
                        response.json()['id'])

            response = await client.post('https://sandbox.melhorenvio.com.br/api/v2/me/shipment/checkout' , json=order_list,
                                          headers=headers)
            response_json = response.json()
            order_list2= [order['id'] for order in response_json['purchase']['orders']]
            return order_list2


    async def get_labels(self, orders: List[str]):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._token}'
        }
        async with AsyncClient() as client:
            payload = {
                'orders': orders
            }

            response = await client.post(f'https://sandbox.melhorenvio.com.br/api/v2/me/shipment/generate',
                                        headers=headers, json=payload)
            if response.status_code == 200:
                 payload['mode'] = 'public'
                 response = await client.post(f'https://sandbox.melhorenvio.com.br/api/v2/me/shipment/print',
                                        headers=headers, json=payload)
                 response_json = response.json()
                 return response_json['url']