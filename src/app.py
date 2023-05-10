import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import HTTPStatusError

from enowshop.middlewares.exception_handler import generic_request_exception_handler
from exception import ValidationException, KeyCloakException, RepositoryException, ExternalConnectionException, \
    ExpirationRecoveryPasswordException


def create_app() -> False:
    app = FastAPI()
    from enowshop.infrastructure.containers import Container
    container = Container()

    from enowshop.endpoints.users import controller as users_module
    users_module.configure(app)

    container.wire(modules=[users_module])

    app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'],
                       allow_headers=['*'])

    app.add_exception_handler(ValidationException, handler=generic_request_exception_handler)
    app.add_exception_handler(KeyCloakException, handler=generic_request_exception_handler)
    app.add_exception_handler(HTTPStatusError, handler=generic_request_exception_handler)
    app.add_exception_handler(RepositoryException, handler=generic_request_exception_handler)
    app.add_exception_handler(ExternalConnectionException, handler=generic_request_exception_handler)
    app.add_exception_handler(ExpirationRecoveryPasswordException, handler=generic_request_exception_handler)
    return app


api_app = create_app()

if __name__ == '__main__':
    uvicorn.run(api_app, host='0.0.0.0', port=8081)
