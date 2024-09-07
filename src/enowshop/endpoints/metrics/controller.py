from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, FastAPI, status, Request, Depends

from enowshop.infrastructure.containers import Container

router = APIRouter(tags=["Métricas"])

@router.get('/metrics', status_code=status.HTTP_200_OK)
@inject
async def get_metrics(request: Request, metrics_service: Container.metrics_services = Depends(Provide[Container.metrics_services])):
    return await metrics_service.get_metrics()

def configure(app: FastAPI):
    app.include_router(router)
