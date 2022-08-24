from typing import Dict, List

from enowshop_models.models.users_password_code_recovery import UsersPasswordCodeRecovery
from sqlalchemy import select, or_, update
from sqlalchemy.orm import selectinload

from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop_models.models.users import Users
from enowshop_models.models.users_address import UserAddress
from enowshop_models.models.users_phones import UsersPhones
from exception import RepositoryException


class UsersRepository(SqlRepository):
    model = Users

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
