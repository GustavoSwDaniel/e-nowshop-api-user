from dependency_injector import containers, providers

from config import Config
from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.domain.sendgrid.client_sendgrid import SendGridClient
from enowshop.endpoints.users.repository import UsersRepository, UserAddressRepository, \
    UsersPhonesRepository, UsersPasswordCodeRecoveryRepository
from enowshop.endpoints.users.service import UsersService
from enowshop.infrastructure.database.database_sql import PostgresDatabase


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    postgres_db = providers.Singleton(PostgresDatabase, database_url=Config.DATABASE_URL)

    # repository
    user_repository = providers.Factory(UsersRepository, session_factory=postgres_db.provided.session)
    user_address_repository = providers.Factory(UserAddressRepository, session_factory=postgres_db.provided.session)
    user_phones_repository = providers.Factory(UsersPhonesRepository, session_factory=postgres_db.provided.session)
    users_password_code_recovery_repository = providers.Factory(UsersPasswordCodeRecoveryRepository,
                                                                session_factory=postgres_db.provided.session)


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
                                       keycloak_service=keycloak_service,
                                       users_password_code_recovery_repository=users_password_code_recovery_repository,
                                       sendgrid_client=sendgrid_client, order_url=Config.ORDER_URL)
