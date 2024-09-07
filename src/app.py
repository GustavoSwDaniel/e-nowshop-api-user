from pathlib import Path
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

    from enowshop.endpoints.orders import controller as orders_module
    orders_module.configure(app)

    from enowshop.endpoints.cars import controller as cars_module
    cars_module.configure(app)

    from enowshop.endpoints.quotes import controller as quotes_module
    quotes_module.configure(app)

    from enowshop.endpoints.metrics import controller as metrics_module
    metrics_module.configure(app)

    from enowshop.endpoints.category import controller as category_module
    category_module.configure(app)

    from enowshop.endpoints.products import controller as product_module
    product_module.configure(app)

    from enowshop.endpoints.stock import controller as stock_module
    stock_module.configure(app)

    from enowshop.domain.s3 import controller as s3_module
    s3_module.configure(app)

    from enowshop.endpoints.report import controller as report_module
    report_module.configure(app)

    from enowshop.endpoints.coupons import controller as coupons_module
    coupons_module.configure(app)

    from enowshop.endpoints.financers import controllers as financers_module
    financers_module.configure(app)

    from enowshop.endpoints.manager import controller as manager_module
    manager_module.configure(app)

    from enowshop.endpoints.permissions import controller as permissions_module
    permissions_module.configure(app)

    from enowshop.endpoints.employees import controller as employees_module
    employees_module.configure(app)

    from enowshop.endpoints.comments import controllers as comment_module
    comment_module.configure(app)


    container.wire(modules=[users_module, orders_module, cars_module, 
                            quotes_module, metrics_module, category_module, product_module, stock_module, s3_module,
                            report_module, coupons_module, financers_module, manager_module,
                            permissions_module, employees_module, comment_module])

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
    uvicorn.run(f"{Path(__file__).stem}:api_app", host='0.0.0.0', port=8081, reload=True)
