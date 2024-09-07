



from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop.infrastructure.models.models.permissions import Permissions


class PermissionsRepository(SqlRepository):
    model = Permissions
