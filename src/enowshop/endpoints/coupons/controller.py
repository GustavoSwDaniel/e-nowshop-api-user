

from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, Request, Response, status
from dependency_injector.wiring import inject
from dependency_injector.wiring import inject, Provide
from enowshop.infrastructure.containers import Container


from enowshop.endpoints.coupons.service import CouponService
from enowshop.endpoints.coupons.schema import CouponSchema, GenerateCouponSchema, RegisterCouponSchema

router = APIRouter(tags=["Cupons"])

@router.post("/generate/coupon", response_model=GenerateCouponSchema)
@inject
async def generate_coupon(request: Request,
                          coupoun_service: CouponService = Depends(Provide[Container.coupoun_service])):
   return await coupoun_service.generate_random_coupon()

@router.post("/coupon", response_model=CouponSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_coupon(request: Request,  coupon_data: RegisterCouponSchema,
                        coupoun_service: CouponService = Depends(Provide[Container.coupoun_service])):
    result = await coupoun_service.create_coupon(coupon_data.dict())
    return result

@router.patch("/deactivate/coupon/{coupon_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def deactivate_coupon(request: Request, coupon_id: int, coupoun_service: CouponService = Depends(Provide[Container.coupoun_service])):
    return await coupoun_service.deactivate_coupon(coupon_id)

@router.get("/coupons", response_model=List[CouponSchema])
@inject
async def get_coupons(request: Request, coupoun_service: CouponService = Depends(Provide[Container.coupoun_service])):
    return await coupoun_service.get_coupons()

def configure(app: FastAPI):
    app.include_router(router)

