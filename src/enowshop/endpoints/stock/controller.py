
from fastapi import APIRouter, FastAPI, status, Request
from starlette.responses import Response
from enowshop.endpoints.stock.schema import StockRegisterSchema, StockSchema, PaginateStockSchema, UpdateStock
from enowshop.endpoints.stock.service import StockService
from enowshop.infrastructure.containers import Container
from fastapi import Depends
from dependency_injector.wiring import Provide, inject

router = APIRouter(tags=["Estoque"])

@router.post('/stock', status_code=status.HTTP_201_CREATED, response_model=StockSchema)
@inject
async def register_stock(request: Request, register_stock: StockRegisterSchema,
                         stock_service: StockService = Depends(Provide[Container.stock_service])):
    return await stock_service.register_stock(register_stock.dict())

@router.get('/stock', status_code=status.HTTP_200_OK, response_model=PaginateStockSchema)
@inject
async def get_all_stock(request: Request,
                        stock_service: StockService = Depends(Provide[Container.stock_service])):
    params = request.query_params
    params = {
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }

    result = await stock_service.get_all_stock(params=params)
    return result

@router.get('/stock/{stock_id}', status_code=status.HTTP_200_OK, response_model=StockSchema)
@inject
async def get_stock_by_id(request: Request, stock_id: str,
                          stock_service: StockService = Depends(Provide[Container.stock_service])):
    return await stock_service.get_stock_by_uuid(stock_id)

@router.put('/stock/{stock_id}', status_code=status.HTTP_200_OK, response_model=StockSchema)
@inject
async def update_stock(request: Request, stock_id: str, update_stock: UpdateStock,
                       stock_service: StockService = Depends(Provide[Container.stock_service])):
    return await stock_service.update_stock(stock_id, update_stock.dict(exclude_none=True))

@router.delete('/stock/{stock_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_stock(request: Request, stock_id: str,
                       stock_service: StockService = Depends(Provide[Container.stock_service])):
    return await stock_service.delete_stock(stock_id)


def configure(app: FastAPI):
    app.include_router(router)
