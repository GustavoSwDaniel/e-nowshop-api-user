from typing import List

from fastapi import APIRouter, FastAPI, status, Request, Depends
from dependency_injector.wiring import inject, Provide

from enowshop.endpoints.category.schema import CategorySchema, CreateCategorySchema
from enowshop.endpoints.category.service import CategoryService
from enowshop.infrastructure.containers import Container

router = APIRouter(tags=["Category"])


@router.post('/category', status_code=status.HTTP_201_CREATED)
@inject
async def create_category(request: Request, category_data: CreateCategorySchema,
                          category_service: CategoryService = Depends(Provide[Container.category_service])):
    return await category_service.create_category(category_data.dict())


@router.get('/category', status_code=status.HTTP_200_OK, response_model=List[CategorySchema])
@inject
async def get_all_categories(request: Request,
                             category_service: CategoryService = Depends(Provide[Container.category_service])):
    return await category_service.get_categories()


@router.get('/category/{category_id}', status_code=status.HTTP_200_OK, response_model=CategorySchema)
@inject
async def get_category_by_id(request: Request, category_id: str,
                             category_service: CategoryService = Depends(Provide[Container.category_service])):
    return await category_service.get_category_by_uuid(category_id)


def configure(app: FastAPI):
    app.include_router(router)
