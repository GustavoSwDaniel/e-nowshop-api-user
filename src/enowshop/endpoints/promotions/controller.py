from typing import List, Union

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, FastAPI, status, Request, Depends
from starlette.responses import Response

from enowshop.endpoints.promotions.schema import PromotionRegisterSchema, UpdatePromotionSchema, \
    PaginatePromotionsSchema
from enowshop.endpoints.promotions.service import PromotionsService
from enowshop.infrastructure.containers import Container

router = APIRouter(tags=["Promomções"])


@router.post('/promotions', status_code=status.HTTP_201_CREATED)
@inject
async def register_promotion(request: Request, register_promotions: PromotionRegisterSchema,
                             promotion_service: PromotionsService = Depends(Provide[Container.promotion_service])):
    return await promotion_service.register_promotion(register_promotions.dict())


@router.get('/promotions', status_code=status.HTTP_200_OK, response_model=PaginatePromotionsSchema)
@inject
async def get_all_promotions(request: Request,
                             promotion_service: PromotionsService = Depends(Provide[Container.promotion_service])):
    query_params = request.query_params
    params = {
        'limit': int(query_params.get('limit', 12)),
        'offset': int(query_params.get('offset', 0))
    }

    return await promotion_service.get_promotions(params=params)


@router.get('/promotion/{promotion_id}', status_code=status.HTTP_200_OK)
@inject
async def get_promotion_by_id(request: Request, promotion_id: str,
                              promotion_service: PromotionsService = Depends(Provide[Container.promotion_service])):
    return await promotion_service.get_promotion(promotion_id)


@router.patch('/promotion/{promotion_uuid}', status_code=status.HTTP_200_OK)
@inject
async def update_promotion_by_id(request: Request, promotion_uuid: str, promotion: UpdatePromotionSchema,
                                 promotion_service: PromotionsService = Depends(Provide[Container.promotion_service])):
    await promotion_service.update_promotion(promotion_uuid=promotion_uuid, promotion=promotion.dict(exclude_none=True))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def configure(app: FastAPI):
    app.include_router(router)