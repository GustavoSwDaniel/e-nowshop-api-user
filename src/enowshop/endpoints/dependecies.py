from fastapi.params import Header
from fastapi import UploadFile
import httpx
from jose.jwt import decode
from jose.exceptions import JWTError
from starlette.exceptions import HTTPException
from pycpfcnpj import cpfcnpj

from config import Config


def format_struct_key(jwt_token: str):
    header = '-----BEGIN PUBLIC KEY-----\n'
    trailer = '\n-----END PUBLIC KEY-----'
    if header not in jwt_token:
        jwt_token = f"{header}{jwt_token}"
    if trailer not in jwt_token:
        jwt_token = f"{jwt_token}{trailer}"

    return jwt_token


def verify_cpf(cpf: str):
    if not cpfcnpj.validate(cpf):
        raise ValueError('Invalid CPF')

async def verify_jwt(authorization: str = Header()):
    jwt_token = authorization.split(" ", 1)[1]
    options = {"verify_signature": True, "verify_aud": False, "exp": True}

    try:
        return decode(jwt_token, format_struct_key(Config.KEYCLOAK_PUBLIC_KEY), algorithms="RS256", options=options)
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized token")

async def verify_acess_token_is_active(access_token, realm, client_id, client_secret):
    url = f"{Config.KEYCLOAK_URL}/auth/realms/{realm}/protocol/openid-connect/token/introspect"
    headers = {'headers': {'Content-Type': 'application/x-www-form-urlencoded'}}
    async with httpx.AsyncClient(**headers) as client:
        response = await client.post(url, data={
                "token": access_token,
                "client_id": client_id,
                "client_secret": client_secret,
            })

        if response.status_code == 200 and response.json().get("active"):
            return True
        return False


async def verify_file_type(file: UploadFile):
    allow_type = ['image/png', 'image/jpeg']

    if file.content_type not in allow_type:
        raise HTTPException(status_code=422, detail="File format no allowed")

async def verify_jwt_manager(authorization: str = Header()):
    jwt_token = authorization.split(" ", 1)[1]
    options = {"verify_signature": True, "verify_aud": False, "exp": True}
    if not await verify_acess_token_is_active(jwt_token, 'manager', 'manager', Config.KEYCLOAK_CLIENT_SECRET_MANAGER):
        return False

    try:
        return decode(jwt_token, format_struct_key(Config.KEYCLOAK_MANAGER_PUBLIC_KEY), algorithms="RS256", options=options)
    except JWTError:
        return False

async def verify_jwt_employee(authorization: str = Header()):
    jwt_token = authorization.split(" ", 1)[1]
    options = {"verify_signature": True, "verify_aud": False, "exp": True}
    if not await verify_acess_token_is_active(jwt_token, 'employees', 'employees', Config.KEYCLOAK_CLIENT_SECRET_EMPLOYEES):
        return False

    try:
        return decode(jwt_token, format_struct_key(Config.KEYCLOAK_EMPLOYESS_PUBLIC_KEY), algorithms="RS256", options=options)
    except JWTError:
        return False

async def verify_role(authorization: str = Header()):
    auth_data_manager = await verify_jwt_manager(authorization=authorization)
    auth_data_employee = await verify_jwt_employee(authorization=authorization)

    if auth_data_manager or auth_data_employee:
        if auth_data_manager and auth_data_manager.get('azp') == 'manager':
            return auth_data_manager
        elif auth_data_employee and auth_data_employee.get('azp') == 'employees':
            return auth_data_employee
    raise HTTPException(status_code=401, detail="Unauthorized token")


async def verify_manager(authorization: str = Header()):
    auth_data = await verify_jwt_manager(authorization=authorization)
    if auth_data.get('azp') == 'manager' and 'employees_manager' in auth_data['realm_access']['roles']:
        return auth_data
    else:
        raise HTTPException(status_code=401, detail="Unauthorized token")
