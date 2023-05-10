from fastapi import APIRouter, FastAPI, status, Request, Depends
from dependency_injector.wiring import inject, Provide
from starlette.responses import Response
from fastapi.params import Header


from enowshop.endpoints.dependecies import verify_jwt
from enowshop.endpoints.users.schema import CreateUserAddressSchema, RefreshTokenSchema, UserRegisterSchema, LoginSchema, LoginResponseSchema, UserDataSchema, \
    UpdateUserData, UpdateUserAddressSchema, UpdateUserPhoneSchema, UpdatePasswordsSchema, EmailRecoveryPassword, \
    RecoveryPasswordsSchema
from enowshop.endpoints.users.service import UsersService
from enowshop.infrastructure.containers import Container

router = APIRouter()


@router.post('/users', status_code=status.HTTP_201_CREATED)
@inject
async def register_user(request: Request, register_user_data: UserRegisterSchema,
                        users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.register_user(register_user_data.dict())
    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/user/auth', status_code=status.HTTP_200_OK, response_model=LoginResponseSchema)
@inject
async def login_user(request: Request, login_data: LoginSchema,
                     users_service: UsersService = Depends(Provide(Container.users_services))):
    response = await users_service.login(login_data=login_data)
    return response


@router.post('/user/refresh/auth', status_code=status.HTTP_200_OK, response_model=LoginResponseSchema)
@inject
async def refresh_token(request: Request, refresh_data: RefreshTokenSchema, user_data_auth=Depends(verify_jwt),
                        users_service: UsersService = Depends(Provide(Container.users_services))):
    response = await users_service.refresh_token(refresh_token=refresh_data.dict().get('refresh_token'),
                                                 keycloak_uuid=user_data_auth.get('sub'))
    return response


@router.get('/user', status_code=status.HTTP_200_OK, response_model=UserDataSchema)
@inject
async def get_user_info(request: Request, user_data_auth=Depends(verify_jwt), headers = Header(None),
                        users_service: UsersService = Depends(Provide(Container.users_services))):
    user_data = await users_service.get_user_info(user_data_auth.get('email'))
    return user_data


@router.patch('/user')
@inject
async def update_user_info(request: Request, update_data: UpdateUserData, user_data_auth=Depends(verify_jwt),
                           users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.update_user_data(uuid_user_auth=user_data_auth.get('sub'), email=user_data_auth.get('email'),
                                         data_update=update_data.dict(exclude_none=True))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch('/user/address/{address_id}')
@inject
async def update_user_address(request: Request, address_id: int, update_data: UpdateUserAddressSchema,
                              user_data_auth=Depends(verify_jwt),
                              users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.update_user_address(address_id=address_id, user_ind=user_data_auth.get('user_id'),
                                            data_update=update_data.dict(exclude_none=True))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch('/user/phones/{phone_id}')
@inject
async def update_user_phones(request: Request, phone_id: int, update_data: UpdateUserPhoneSchema,
                             user_data_auth=Depends(verify_jwt),
                             users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.update_user_phone(phone_id=phone_id, user_ind=user_data_auth.get('user_id'),
                                          data_update=update_data.dict(exclude_none=True))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch('/user/password')
@inject
async def update_password(request: Request, update_data: UpdatePasswordsSchema, user_data_auth=Depends(verify_jwt),
                          users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.update_password(email=user_data_auth.get('email'), keycloak_user_id=user_data_auth.get('sub'),
                                        update_password=update_data.dict())


@router.post('/user/recovery', status_code=status.HTTP_200_OK)
@inject
async def create_recovery_password_code(request: Request, email: EmailRecoveryPassword,
                                        users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.create_recovery_password_code(email=email.dict().get('email'))
    return Response(status_code=status.HTTP_200_OK)


@router.patch('/user/recovery/password/{recovery_code}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def recovery_password(request: Request, recovery_code: str, new_password: RecoveryPasswordsSchema,
                            users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.recovery_password(recovery_code=recovery_code, new_password=new_password.dict())
    return Response(status_code=status.HTTP_200_OK)

@router.post('/user/address', status_code=status.HTTP_201_CREATED)
@inject
async def create_user_address(request: Request, address_data: CreateUserAddressSchema,
                              user_data_auth=Depends(verify_jwt),
                              users_service: UsersService = Depends(Provide(Container.users_services))):
    await users_service.create_user_address(keycloak_uuid=user_data_auth.get('sub'), data=address_data.dict())
    return Response(status_code=status.HTTP_201_CREATED)

def configure(app: FastAPI):
    app.include_router(router)
