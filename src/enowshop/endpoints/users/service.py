import random
import string
from datetime import datetime, timedelta
from typing import Dict

from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.domain.sendgrid.client_sendgrid import SendGridClient
from enowshop.endpoints.users.repository import UsersRepository, UserAddressRepository, UsersPhonesRepository, \
    UsersPasswordCodeRecoveryRepository
from enowshop.endpoints.users.schema import LoginSchema
from enowshop_models.models.users import Users
from exception import ExternalConnectionException, ExpirationRecoveryPasswordException


class UsersService:
    def __init__(self, users_repository: UsersRepository, users_address_repository: UserAddressRepository,
                 users_phones_repository: UsersPhonesRepository, keycloak_service: KeycloakService,
                 users_password_code_recovery_repository: UsersPasswordCodeRecoveryRepository,
                 sendgrid_client: SendGridClient):
        self.users_repo = users_repository
        self.user_address_repo = users_address_repository
        self.users_phones_repo = users_phones_repository
        self.users_password_code_repo = users_password_code_recovery_repository
        self.keycloak_service = keycloak_service
        self.sendgrid_client = sendgrid_client

    async def check_if_email_or_cpf_already_registered(self, email: str, cpf: str):
        await self.users_repo.verify_email_or_cpf_already_register(email=email, cpf=cpf)

    async def register_user(self, user_data: Dict):
        await self.check_if_email_or_cpf_already_registered(email=user_data.get('email'), cpf=user_data.get('cpf'))

        password = user_data.pop('password')
        address = user_data.pop('address')
        phones = user_data.pop('phones')
        user = await self.users_repo.create(user_data)
        address['user_id'] = user.id
        list(map(lambda item: item.update({'user_id': user.id}), phones))
        await self.users_phones_repo.create_phones_with_bulk_operator(phones)
        await self.user_address_repo.create(address)

        keycloak_uuid = await self.keycloak_service.create_user_by_admin_cli(data=user_data, password=password,
                                                                             user_id=user.id)

        await self.users_repo.update(pk=user.id, values={'keycloak_uuid': keycloak_uuid})

    async def login(self, login_data: LoginSchema) -> Dict:
        response = await self.keycloak_service.auth_user(username=login_data.username,
                                                         password=login_data.password)
        return response

    async def get_user_info(self, email: str) -> Users:
        user_date = await self.users_repo.filter_by_with_address({'email': email})
        return user_date

    async def update_user_data(self, uuid_user_auth: str, email: str, data_update: Dict) -> None:
        await self.users_repo.update_by_email(email=email, values=data_update)
        await self.keycloak_service.update_user_data(uuid_user=uuid_user_auth, update_data=data_update)

    async def update_user_address(self, address_id: int, user_ind: int, data_update: Dict) -> None:
        await self.user_address_repo.update_by_id_and_user_id(pk=address_id, user_id=user_ind, values=data_update)

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
        await self.keycloak_service.change_password(email=user.email, keycloak_user_id=user.keycloak_uuid,
                                                    update_password=new_password, recovery_mode=True)