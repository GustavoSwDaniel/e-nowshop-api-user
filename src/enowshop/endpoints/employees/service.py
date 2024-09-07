from datetime import datetime, timedelta, timezone
from typing import Dict

import bcrypt
from jose import JWTError, jwt

from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.endpoints.employees.repository import EmployeesRepository
from enowshop.endpoints.employees.schema import LoginSchema
from enowshop.infrastructure.models.models.users import Users


class EmployeesService:
    def __init__(self, employees_repository: EmployeesRepository,
                 keycloak_service: KeycloakService,):
        self.employees_repo = employees_repository
        self.keycloak_service = keycloak_service

    async def check_if_email_or_cpf_already_registered(self, email: str, cpf: str):
        await self.employees_repo.verify_email_or_cpf_already_register(email=email, cpf=cpf)

    async def register_employees(self, user_data: Dict):
        password = user_data.pop('password')
        address = user_data.pop('address')
        phones = user_data.pop('phones')
        user = await self.employees_repo.create(user_data)
        address['user_id'] = user.id
        list(map(lambda item: item.update({'user_id': user.id}), phones))

        keycloak_uuid = await self.keycloak_service.create_user_by_admin_cli(data=user_data, password=password,
                                                                             employee_id=user.id)

        await self.employees_repo.update(pk=user.id, values={'keycloak': keycloak_uuid})

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7', algorithm='HS256')
        return encoded_jwt


    async def login(self, login_data: LoginSchema) -> Dict:
        employee = await self.employees_repo.get_employment_info_by_email(params={'email': login_data.username})
        if not employee:
            raise Exception('Error')
        
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), employee.password.encode('utf-8')):
            raise Exception('Error')
        
        response = {}

        response['name'] = employee.name
        response['email'] = employee.email
        response['uuid'] = employee.uuid
        response['position'] = employee.permission
        response['access_token'] = self.create_access_token(data=response)

        return response

    async def logout_employee(self, token: str, client_id: str, client_secret: str):
        await self.keycloak_service.logout(token=token, client_id=client_id,
                                           client_secret=client_secret,
                                           realm='manager')
