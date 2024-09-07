from typing import List, Union


from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, FastAPI, status, Request, Depends
from starlette.responses import Response

from enowshop.endpoints.products.schema import ProductRegisterSchema, ProductsSchema, UpdateProductSchema, \
    PaginateProductsSchema, PaginateProductsWithPromotionsSchema, CreateProductReponseSchema
from enowshop.endpoints.products.service import ProductsService
from enowshop.infrastructure.containers import Container

router = APIRouter(tags=["Produtos"])


@router.post('/products', status_code=status.HTTP_201_CREATED, response_model=CreateProductReponseSchema)
@inject
async def register_product(request: Request, register_products: ProductRegisterSchema,
                           product_service: ProductsService = Depends(Provide[Container.product_service])):
    product = await product_service.register_product(register_products.dict())
    return product


@router.get('/products', status_code=status.HTTP_200_OK, response_model=PaginateProductsSchema)
@inject
async def get_all_products(request: Request, category: Union[str, None] = None,
                           product_service: ProductsService = Depends(Provide[Container.product_service])):
    params = request.query_params
    params = {
        'category': params.get('category', None),
        'min_price': params.get('min_price', None),
        'max_price': params.get('max_price', None),
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
        'name': params.get('name', None),
        'order_by': params.get('order_by', None),
        'order': params.get('order', None),
        'all': params.get('all', False),
        'stock': params.get('stock', False),
    }
    
    products =  await product_service.get_all_products_with_category(params=params)
    return products


@router.get('/products/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductsSchema)
@inject
async def get_product_by_id(request: Request, product_id: str,
                            product_service: ProductsService = Depends(Provide[Container.product_service])):
    params = request.query_params
    params = {
        'stock': params.get('stock', False),
        'recomendation': params.get('recomendation', True)
    }
    return await product_service.get_product_by_uuid(product_id, params)


@router.patch('/products/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_product_by_id(request: Request, product_id: str, product: UpdateProductSchema,
                               product_service: ProductsService = Depends(Provide[Container.product_service])):
    await product_service.update_product_by_uuid(product_id, product.dict(exclude_none=True))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/products/{product_id}/deactivate', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def deactivate_product(request: Request, product_id: str,
                                             product_service: ProductsService = Depends(Provide[Container.product_service])):
    await product_service.change_status_active(product_id, action='activate')
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/products/promotions/{promotion_uuid}', status_code=status.HTTP_200_OK, response_model=PaginateProductsWithPromotionsSchema)
@inject
async def get_products_by_promotions(request: Request, promotion_uuid: str,
                                     product_service: ProductsService = Depends(Provide[Container.product_service])):
    params = request.query_params
    params = {
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0))
    }

    return await product_service.get_products_by_promotion(promotion_uuid=promotion_uuid, params=params)

def configure(app: FastAPI):
    app.include_router(router)
