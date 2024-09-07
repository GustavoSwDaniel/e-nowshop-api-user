

from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, Request, Response
from dependency_injector.wiring import inject
from dependency_injector.wiring import inject, Provide
from enowshop.infrastructure.containers import Container


from enowshop.endpoints.permissions.schema import PermissionSchema, PermissionResponseSchema
from enowshop.endpoints.permissions.service import PermissionsService

router = APIRouter(tags=["Permissões"])

@router.post("/permissions", response_model=PermissionResponseSchema)
@inject
async def create_permission(request: Request, data: PermissionSchema,
                     permissions_service: PermissionsService = Depends(Provide[Container.permissions_service])):
    return await permissions_service.create_permission(data.dict())


@router.get("/permissions", response_model=List[PermissionResponseSchema])
@inject
async def get_reports(request: Request, 
                     permissions_service: PermissionsService = Depends(Provide[Container.permissions_service])):
    return await permissions_service.get_permissions()

def configure(app: FastAPI):
    app.include_router(router)

