import crypt
import random
import string
from datetime import datetime, timedelta, timezone
import time
from typing import Dict, Union
import bcrypt

from jose import JWTError, jwt

from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.domain.sendgrid.client_sendgrid import SendGridClient
from enowshop.endpoints.users.repository import UsersRepository, UserAddressRepository, UsersPhonesRepository, \
    UsersPasswordCodeRecoveryRepository
from enowshop.endpoints.users.schema import LoginSchema
from enowshop.infrastructure.models.models.users import Users
from exception import ExternalConnectionException, ExpirationRecoveryPasswordException
import httpx
import re

from enowshop.endpoints.cars.repository import CarsRepository


class UsersService:
    def __init__(self, users_repository: UsersRepository, users_address_repository: UserAddressRepository,
                 users_phones_repository: UsersPhonesRepository,
                 users_password_code_recovery_repository: UsersPasswordCodeRecoveryRepository, cart_repository: CarsRepository,
                 sendgrid_client: SendGridClient, order_url: str):
        self.users_repo = users_repository
        self.user_address_repo = users_address_repository
        self.users_phones_repo = users_phones_repository
        self.users_password_code_repo = users_password_code_recovery_repository
        self.cart_repositoy = cart_repository
        self.sendgrid_client = sendgrid_client
        self.order_url = order_url

    async def check_if_email_or_cpf_already_registered(self, email: str, cpf: str):
        await self.users_repo.verify_email_or_cpf_already_register(email=email, cpf=cpf)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7', algorithm='HS256')
        return encoded_jwt

    async def register_user(self, user_data: Dict):
        await self.check_if_email_or_cpf_already_registered(email=user_data.get('email'), cpf=user_data.get('cpf'))

        user_data['cpf'] = re.sub(r'[.-]', '', user_data['cpf'])

        user_data['password'] = bcrypt.hashpw(user_data.pop('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        address = user_data.pop('address')
        phones = user_data.pop('phones')
        user = await self.users_repo.create(user_data)
        address['user_id'] = user.id
        list(map(lambda item: item.update({'user_id': user.id}), phones))
        await self.users_phones_repo.create_phones_with_bulk_operator(phones)
        await self.user_address_repo.create(address)

    async def login(self, login_data: LoginSchema) -> Dict:
        
        response = {}

        user_data = await self.users_repo.get_user_info_by_email(params={'email': login_data.username})
        if not user_data:
            raise Exception('User not found')
        
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user_data.password.encode('utf-8')):
            raise Exception('Error')

        response['name'] = user_data.name
        response['last_name'] = user_data.last_name
        response['email'] = user_data.email
        response['uuid'] = user_data.uuid
        
        response['access_token'] = self.create_access_token(data=response)

        return response

    async def get_user_info(self, email: str) -> Users:
        user_date = await self.users_repo.filter_by_with_address({'email': email})
        return user_date

    async def update_user_data(self, uuid_user_auth: str, email: str, data_update: Dict) -> None:
        await self.users_repo.update_by_email(email=email, values=data_update)

    async def update_user_address(self, address_id: int, user_uuid: int, data_update: Dict) -> None:
        user = await self.users_repo.filter_by({'uuid': user_uuid})
        await self.user_address_repo.update_by_id_and_user_id(pk=address_id, user_id=user.id, values=data_update)

    async def update_user_phone(self, phone_id: int, user_ind: int, data_update: Dict) -> None:
        await self.users_phones_repo.update_by_id_and_user_id(pk=phone_id, user_id=user_ind, values=data_update)

    async def update_password(self, email: str, keycloak_user_id: str,update_password: Dict) -> None:
        await self.keycloak_service.change_password(email=email, keycloak_user_id=keycloak_user_id,
                                                    update_password=update_password)

    async def create_recovery_password_code(self, email: str):
        user = await self.users_repo.filter_by({'email': email})
        users_password_code = None
        try:
            recovery_code = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
            users_password_code = await self.users_password_code_repo.create(
                {'code': recovery_code,
                 'user_id': user.id})
            await self.sendgrid_client.send_email(email=email, send_data={'code_recovery': recovery_code})
        except ExternalConnectionException:
            await self.users_password_code_repo.delete(users_password_code)
            raise ExternalConnectionException('Error in send email with recovery code')

    @staticmethod
    def check_recovery_password_is_expired(recovery_code_created_at: datetime):
        if recovery_code_created_at > recovery_code_created_at + timedelta(minutes=30):
            raise ExpirationRecoveryPasswordException('Recovery code is expired')

    async def recovery_password(self, recovery_code: str, new_password):
        recovery_code = await self.users_password_code_repo.filter_by({'code': recovery_code})
        user = await self.users_repo.filter_by({'id': recovery_code.user_id})

        self.check_recovery_password_is_expired(recovery_code_created_at=recovery_code.created_at)
        password = bcrypt.hashpw(new_password['new_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        await self.users_repo.update(pk=user.id, values={'password': password})


    async def create_user_address(self, keycloak_uuid: int, data: Dict):
        user = await self.users_repo.filter_by({'keycloak_uuid': keycloak_uuid})
        data['user_id'] = user.id
        await self.user_address_repo.create(data)
    
    async def refresh_token(self, refresh_token: str, keycloak_uuid: str) -> Dict:
        


        return {"ref": "ref"}