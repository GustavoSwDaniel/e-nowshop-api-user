



from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop.infrastructure.models.models.reports import Reports


class ReportsRepository(SqlRepository):
    model = Reports
