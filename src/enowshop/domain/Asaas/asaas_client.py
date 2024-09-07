from typing import Dict, Callable
from httpx import AsyncClient
from datetime import datetime, timedelta

class AsaasClient:
    def __init__(self, token: str, url: str) -> None:
        self.token = token
        self.url = url
    
    def _build_pix_payload(self, payload: Dict, customer: str) -> Dict:
        return {
            "customer": payload['customer'],
            "billingType": 'PIX',
            "value": payload['total_value'],
            "dueDate": (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
        }
    
    def _build_billet_payload(self, payload: Dict, customer: str) -> Dict:
        return {
            "customer": payload['customer'],
            "billingType": "BOLETO",
            "value": payload['total_value'],
            "dueDate": (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
        }
    
    def _build_paycard_payload(self, payload: Dict) -> Dict:
        return {
            "billingType": "CREDIT_CARD",
            "creditCard": {
                "holderName": payload['card_info']['name'],
                "number": payload['card_info']['number'].replace(' ', ''),
                "expiryMonth": payload['card_info']['expiry_month'],
                "expiryYear": f'20{payload["card_info"]["expiry_year"]}',
                "ccv": payload['card_info']['cvv']
            },
            "creditCardHolderInfo": {
                "name": payload['card_holder_info']['name'],
                "cpfCnpj": payload['card_holder_info']['cpf'],
                "email": payload['card_holder_info']['email'],
                "postalCode": payload['card_holder_info']['cep'],
                "addressNumber": str(payload['card_holder_info']['number']),
                "phone": payload['card_holder_info']['phone'],
            },
            "customer": payload['customer'],
            "value": payload['total_value'],
            "dueDate": (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d"),
        }
    
    def build_payload_customer(self, customer_info: Dict) -> Dict:
        return {
            "name": customer_info['name'],
            "cpfCnpj": customer_info['cpf'],
            "mobilePhone": customer_info['phone']
        }

    async def create_customer(self, customer_data: Dict) -> Dict:
        customer_info = self.build_payload_customer(customer_data)
        async with AsyncClient() as client:
            response = await client.post(f'{self.url}/api/v3/customers', 
                                         headers={'access_token': self.token,
                                                  "accept": "application/json"},
                                                  json=customer_info)
            return response.json()
    
    async def _create_order_paycard(self, order_data: Dict) -> Dict:
        order_info = self._build_paycard_payload(order_data)
        async with AsyncClient() as client:
            response = await client.post(f'{self.url}/api/v3/payments', 
                                         headers={'access_token': self.token,
                                                  "accept": "application/json"},
                                                    json=order_info)
            return response.json()
    
    
    async def _create_order_pix(self, order_data: Dict) -> Dict:
        order_info = self._build_pix_payload(order_data, order_data['customer'])
        async with AsyncClient() as client:
            response = await client.post(f'{self.url}/api/v3/payments', 
                                         headers={'access_token': self.token}, json=order_info)
            result_qrcode = await client.get(f'{self.url}/api/v3/payments/{response.json()["id"]}/pixQrCode',
                                             headers={'access_token': self.token})
            
            result = response.json()
            data = result_qrcode.json()
            data['encodedImage'] = f'data:image/png;base64, {data["encodedImage"]}'
            data['code'] = data['payload']
            data['id'] = result['id']
            data['payload'] = result
            data['value'] = result['value']
            data['billingType'] = result['billingType']
            return data
    
    
    async def _create_order_billet(self, order_data: Dict) -> Dict:
        order_info = self._build_billet_payload(order_data, order_data['customer'])
        async with AsyncClient() as client:
            response = await client.post(f'{self.url}/api/v3/payments', 
                                         headers={'access_token': self.token}, json=order_info)
            
            response_billet = await client.get(f'{self.url}/api/v3/payments/{response.json()["id"]}/identificationField',
                                             headers={'access_token': self.token})

            result = response.json()
            result_billet = response_billet.json()
            return {
                "billet_url": result['bankSlipUrl'],
                "identification_field": result_billet['identificationField'],
                "bar_code": result_billet['barCode'],
                "value": result['value'],
                "billingType": result['billingType'],
                "id": result['id'],


            }
            
    
    
    def get_payment_type(self, payment_type: str) -> Callable:
        return {
            'card': self._create_order_paycard,
            'pix': self._create_order_pix,
            'billet': self._create_order_billet
        }[payment_type]
    
    async def create_order(self, order_data: Dict) -> Dict:
        payment_type = order_data['payment_method']
        return await self.get_payment_type(payment_type)(order_data)