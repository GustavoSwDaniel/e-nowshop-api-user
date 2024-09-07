from typing import Dict, List

from enowshop.infrastructure.models.models.users_password_code_recovery import UsersPasswordCodeRecovery
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload

from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop.infrastructure.models.models.users import Users
from enowshop.infrastructure.models.models.users_address import UserAddress
from enowshop.infrastructure.models.models.users_phones import UsersPhones
from exception import RepositoryException


class UsersRepository(SqlRepository):
    model = Users

    async def filter_by_with_address(self, user_keycloack_uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).options(selectinload(Users.user_address))
                .where(self.model.keycloak_uuid == user_keycloack_uuid)
                .where(self.model.user_address.any(UserAddress.main== True)))
            user = result.scalars().first()
            if not user:
                raise RepositoryException('User does not found')
            return user
    
    async def get_user_with_phone(self, uuid) -> Users:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).options(selectinload(Users.user_address)).options(selectinload(Users.user_phones))
                .where(self.model.uuid == uuid)
                .where(self.model.user_address.any(UserAddress.main==True)))
            user = result.scalars().first()
            if not user:
                raise RepositoryException('User does not found')
            return user
        
    async def get_user_by_id(self, user_id) -> Users:
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).options(selectinload(Users.user_address)).options(selectinload(Users.user_phones))
                .where(self.model.id == user_id)
                .where(self.model.user_address.any(UserAddress.main==True)))
            user = result.scalars().first()
            if not user:
                raise RepositoryException('User does not found')
            return user

    async def verify_email_or_cpf_already_register(self, email: str, cpf: str):
        async with self.session_factory() as session:

            result = await session.execute(
                select(self.model).
                    where(or_(self.model.email == email, self.model.cpf == cpf))
            )
        if result.scalars().first():
            raise RepositoryException('That email or cpf is already registered')

    async def filter_by_with_address(self, params):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(**params).options(
                selectinload(self.model.user_address),
                selectinload(self.model.user_phones)))
            return result.scalars().first()

    async def update_by_email(self, email: str, values: Dict):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(self.model.email == email).values(**values))
            await session.commit()

    async def get_user_info_by_email(self, params) -> Users:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(**params))
            result = result.scalars().first()

        if not result:
            raise RepositoryException('Email not already registered')

        return result
    
    async def get_user_info_by_keycloak_uuid(self, params) -> Users:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(**params))
            result = result.scalars().first()

        if not result:
            raise RepositoryException('Keycloak uuid not already registered')

        return result


class UserAddressRepository(SqlRepository):
    model = UserAddress

    async def update_by_id_and_user_id(self, pk: int, user_id: int, values):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(
                self.model.id == pk, self.model.user_id == user_id).values(**values))
            await session.commit()


class UsersPhonesRepository(SqlRepository):
    model = UsersPhones

    async def create_phones_with_bulk_operator(self, phones: List):
        async with self.session_factory() as session:
            model = session.add_all([self.model(**phone) for phone in phones])
            await session.commit()
            return model

    async def update_by_id_and_user_id(self, pk: int, user_id: int, values):
        async with self.session_factory() as session:
            await session.execute(update(self.model).where(
                self.model.id == pk, self.model.user_id == user_id).values(**values))
            await session.commit()


class UsersPasswordCodeRecoveryRepository(SqlRepository):
    model = UsersPasswordCodeRecovery
