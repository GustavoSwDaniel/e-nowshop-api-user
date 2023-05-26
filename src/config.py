import os


class Config:
    BROKER_URL = os.getenv('BROKER_URL', 'localhost:9092')

    DATABASE_URL = os.getenv('A-POSTGRES_DATABASE_URL')

    KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
    KEYCLOAK_REALMS = os.getenv('KEYCLOAK_REALMS', 'users')
    KEYCLOAK_PUBLIC_KEY = os.getenv('PUBLIC_KEY')
    KEYCLOAK_CLIENT_ID_ADMIN_CLI = os.getenv('KEYCLOAK_CLIENT_ID_ADMIN_CLI', 'admin-cli')
    KEYCLOAK_CLIENT_SECRET_ADMIN_CLI = str(os.getenv('KEYCLOAK_CLIENT_SECRET_ADMIN_CLI'))
    KEYCLOAK_CLIENT_SECRET_USERS = str(os.getenv('KEYCLOAK_CLIENT_SECRET_USERS'))
    KEYCLOAK_CLIENT_ID_USERS = os.getenv('KEYCLOAK_CLIENT_ID_USERS', 'users')

    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_URL = os.getenv('SENDGRID_URL', 'https://api.sendgrid.com/v3/mail/send')
    SENDGRID_ORiGIN_EMAIL = os.getenv('SENDGRID_ORiGIN_EMAIL', 'verificacaoenowshop@e-nowshop.com.br')
    FRONT_END_LINK = os.getenv('FRONT_END_LINK', 'http://localhost:3000')
