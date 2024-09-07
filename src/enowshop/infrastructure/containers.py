from dependency_injector import containers, providers
from zeep import Client as SoapClient, Transport
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

from config import Config

from enowshop.endpoints.promotions.service import PromotionsService
from enowshop.endpoints.products.repository import ProductsRepository, CategoryProductsRepository
from enowshop.endpoints.category.service import CategoryService
from enowshop.endpoints.orders.repository import OrderItemsRepository
from enowshop.endpoints.orders.repository import OrdersRepository
from enowshop.endpoints.category.repository import CategoryRepository
from enowshop.endpoints.employees.repository import EmployeesRepository
from enowshop.endpoints.promotions.repository import PromotionsRepository
from enowshop.endpoints.metrics.repository import OrdersItemsRepository, UsersRepository
from enowshop.endpoints.stock.repository import StockRepository
from enowshop.endpoints.stock.service import StockService


from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.domain.sendgrid.client_sendgrid import SendGridClient
from enowshop.domain.s3.s3_client import S3Client
from enowshop.domain.s3.service import S3Service

from enowshop.endpoints.users.repository import UsersRepository, UserAddressRepository, \
    UsersPhonesRepository, UsersPasswordCodeRecoveryRepository
from enowshop.endpoints.metrics.repository import UsersRepository as UsersMetricsRepository
from enowshop.endpoints.metrics.repository import OrdersRepository as OrderMetricsRepository
from enowshop.endpoints.metrics.repository import OrdersItemsRepository as OrdersItemsMetricsRepository
from enowshop.endpoints.users.service import UsersService
from enowshop.endpoints.orders.service import OrdersService
from enowshop.endpoints.quotes.service import QuotesService
from enowshop.endpoints.cars.service import CarsService
from enowshop.domain.correios.client import CorreiosClient
from enowshop.endpoints.cars.repository import CarsRepository, CartItensRepository
from enowshop.endpoints.manager.service import ManagerService
from enowshop.endpoints.generic.service import GenericService
from enowshop.endpoints.employees.service import EmployeesService
from enowshop.endpoints.metrics.service import MetricsService
from enowshop.endpoints.products.service import ProductsService
from enowshop.endpoints.comments.service import CommentService

from enowshop.infrastructure.database.database_sql import PostgresDatabase
from enowshop.infrastructure.database.nosql import MongoDatabase
from enowshop.domain.melhor_envio.melhor_envio import MelhorEnvio
from enowshop.domain.Asaas.asaas_client import AsaasClient
from enowshop.endpoints.report.service import ReportService
from enowshop.domain.pdf.pdf import PDF
from enowshop.endpoints.report.repository import ReportsRepository
from enowshop.endpoints.coupons.repository import CouponsProductsRepository, CouponsRepository
from enowshop.endpoints.coupons.service import CouponService
from enowshop.endpoints.financers.service import FinancersService
from enowshop.endpoints.financers.repository import FinancersRepository
from enowshop.endpoints.permissions.repository import PermissionsRepository
from enowshop.endpoints.comments.repository import CommentsRepository
from enowshop.endpoints.permissions.service import PermissionsService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    postgres_db = providers.Singleton(PostgresDatabase, database_url=Config.DATABASE_URL)
    mongo_database = providers.Singleton(MongoDatabase, database=Config.MONGO_DATABASE_DB,
                                         host=Config.MONGO_DATABASE_HOST, port=Config.MONGO_DATABASE_PORT,
                                         user=Config.MONGO_DATABASE_USER, password=Config.MONGO_DATABASE_PASSWORD,
                                         authentication_source=Config.MONGO_DATABASE_AUTH_SOURCE)
    
    melhor_envio = providers.Singleton(MelhorEnvio, token=Config.MELHOR_ENVIO_TOKEN, origin_cep=Config.MELHOR_ENVIO_ORIGIN_CEP)
    asaas_client = providers.Singleton(AsaasClient, token=Config.ASAAS_ACCESS_TOKEN, url=Config.ASAAS_URL)
    # repository

    coupons_repository = providers.Factory(CouponsRepository, session_factory=postgres_db.provided.session)
    coupons_products_repository = providers.Factory(CouponsProductsRepository, session_factory=postgres_db.provided.session)
    user_repository = providers.Factory(UsersRepository, session_factory=postgres_db.provided.session)
    user_address_repository = providers.Factory(UserAddressRepository, session_factory=postgres_db.provided.session)
    user_phones_repository = providers.Factory(UsersPhonesRepository, session_factory=postgres_db.provided.session)
    users_password_code_recovery_repository = providers.Factory(UsersPasswordCodeRecoveryRepository,
                                                                session_factory=postgres_db.provided.session)
    orders_repository = providers.Factory(OrdersRepository, session_factory=postgres_db.provided.session)
    order_items_repository = providers.Factory(OrderItemsRepository, session_factory=postgres_db.provided.session)
    products_repository = providers.Factory(ProductsRepository, session_factory=postgres_db.provided.session)
    cars_repository = providers.Factory(CarsRepository, session_factory=postgres_db.provided.session)
    category_repository = providers.Factory(CategoryRepository, session_factory=postgres_db.provided.session)
    category_product_repository = providers.Factory(CategoryProductsRepository,
                                                    session_factory=postgres_db.provided.session)
    car_items_repository = providers.Factory(CartItensRepository, session_factory=postgres_db.provided.session)

    promotions_repository = providers.Factory(PromotionsRepository, session_factory=postgres_db.provided.session)

    employees_repository = providers.Factory(EmployeesRepository, session_factory=postgres_db.provided.session)
    order_metrics_repository = providers.Factory(OrderMetricsRepository, session_factory=postgres_db.provided.session)
    order_items_metrics_repository = providers.Factory(OrdersItemsMetricsRepository,
                                               session_factory=postgres_db.provided.session)
    users_metrics_repository = providers.Factory(UsersMetricsRepository, session_factory=postgres_db.provided.session)

    stock_repository = providers.Factory(StockRepository, session_factory=postgres_db.provided.session)

    reports_repository = providers.Factory(ReportsRepository, session_factory=postgres_db.provided.session)
    financers_repository = providers.Factory(FinancersRepository, session_factory=postgres_db.provided.session)

    permissions_repository = providers.Factory(PermissionsRepository, session_factory=postgres_db.provided.session)
    comments_repository = providers.Factory(CommentsRepository, session_factory=postgres_db.provided.session)
    # zeep client soap
    transport = Transport(timeout=2)
    zeep_client = providers.Singleton(SoapClient, wsdl=Config.URL_CORREIOS, transport=transport)

    # correios
    correios = providers.Singleton(CorreiosClient, client_soap=zeep_client)

    #pubnub
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key =  Config.PUBNUB_SUBSCRIBE_KEY
    pnconfig.publish_key = Config.PUBNUB_PUBLISH_KEY
    pnconfig.ssl = False
    pnconfig.user_id = "payment-agent"
    pn = providers.Factory(PubNub, pnconfig)

    # s3
    s3_client = providers.Factory(S3Client, s3_bucket_name=Config.S3_BUCKET_NAME,
                                  aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                                  aws_region_name=Config.AWS_REGION_NAME)


    # services
    keycloak_service = providers.Factory(KeycloakService, client_id_admin_cli=Config.KEYCLOAK_CLIENT_ID_ADMIN_CLI,
                                         client_id=Config.KEYCLOAK_CLIENT_ID_USERS,
                                         client_secret_admin_cli=Config.KEYCLOAK_CLIENT_SECRET_ADMIN_CLI,
                                         client_secret=Config.KEYCLOAK_CLIENT_SECRET_USERS,
                                         keycloak_url=Config.KEYCLOAK_URL, realm=Config.KEYCLOAK_REALMS)
    sendgrid_client = SendGridClient(sendgrid_url=Config.SENDGRID_URL, sendgrid_api_key=Config.SENDGRID_API_KEY,
                                     origin_email=Config.SENDGRID_ORiGIN_EMAIL, link_frontend=Config.FRONT_END_LINK)
    users_services = providers.Factory(UsersService, users_repository=user_repository,
                                       users_address_repository=user_address_repository,
                                       users_phones_repository=user_phones_repository,
                                       cart_repository=cars_repository,
                                       users_password_code_recovery_repository=users_password_code_recovery_repository,
                                       sendgrid_client=sendgrid_client, order_url=Config.ORDER_URL)

    quotes_service = providers.Factory(QuotesService, correios_client=correios, 
                                       products_repository=products_repository,
                                       user_address_repository=user_address_repository,
                                       origin_cep=Config.ORIGIN_CEP)
    cars_service = providers.Factory(CarsService, cars_repository=cars_repository,
                                     products_repository=products_repository,
                                     user_repository=user_repository,
                                     car_items_repository=car_items_repository,
                                     melhor_envio=melhor_envio,
                                     cupom_repository=coupons_repository,
                                     cupom_products_repository=coupons_products_repository)
    orders_service = providers.Factory(OrdersService, orders_repository=orders_repository,
                                   products_repository=products_repository,
                                   order_items_repository=order_items_repository,
                                   user_reponsitory=user_repository,
                                   user_address_repository=user_address_repository,
                                   payment_access_token=Config.PAYMENT_ACCESS,
                                   asaas_client=asaas_client,
                                   car_service=cars_service,
                                   stock_repository=stock_repository,
                                   financers_repository=financers_repository,
                                   melhor_envio=melhor_envio)
    
    s3_service = providers.Factory(S3Service, s3_client=s3_client)

    category_service = providers.Factory(CategoryService, category_repository=category_repository)
    product_service = providers.Factory(ProductsService, category_repository=category_repository,
                                        products_repository=products_repository,
                                        category_products_repository=category_product_repository,
                                        promotion_products=promotions_repository,
                                        stock_repository=stock_repository)
    promotion_service = providers.Factory(PromotionsService, promotions_repository=promotions_repository)

    employees_services = providers.Factory(EmployeesService, employees_repository=employees_repository,
                                           keycloak_service=keycloak_service)
    manager_service = providers.Factory(ManagerService, employees_repository=employees_repository,
                                        keycloak_service=keycloak_service)
    generic_service = providers.Factory(GenericService, keycloak_service=keycloak_service)

    metrics_services = providers.Factory(MetricsService, order_repository=users_metrics_repository,
                                         order_items_repository=order_items_metrics_repository,
                                         users_repository=users_metrics_repository)
    
    stock_service = providers.Factory(StockService, stock_repository=stock_repository,
                                      product_repository=products_repository)
    pdf_service = providers.Factory(PDF)
    report_service = providers.Factory(ReportService, pdf_service=pdf_service, orders_repository=orders_repository,
                                       order_items_repository=order_items_repository, s3_service=s3_service,
                                       report_repository=reports_repository)
    
    coupoun_service = providers.Factory(CouponService, coupon_repository=coupons_repository,
                                        coupon_product_repository=coupons_products_repository,
                                        product_repository=products_repository)
    
    finace_service = providers.Factory(FinancersService, financers_repository=financers_repository,
                                       pdf_service=pdf_service)

    permissions_service = providers.Factory(PermissionsService, permissions_repository=permissions_repository)
    comment_service = providers.Factory(CommentService, 
                                        comments_repository=comments_repository, 
                                        user_repository=user_repository, 
                                        order_items_repository=order_items_repository)