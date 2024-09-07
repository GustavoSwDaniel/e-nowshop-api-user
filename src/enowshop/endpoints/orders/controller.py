import io
from typing import Union
from fastapi import APIRouter, Depends, Request, FastAPI, status
from fastapi.responses import JSONResponse, StreamingResponse

from config import Config
from enowshop.endpoints.orders.schema import CreateOrderSchema, DownloadBillet, OrderCreatedSchema, OrderReponse, UpdateStatusSchema, OrdersPaginateSchema, UpdateStatusSendoSchema
from enowshop.endpoints.orders.service import OrdersService
from dependency_injector.wiring import inject, Provide
from distutils.util import strtobool


from enowshop.infrastructure.containers import Container
from enowshop.endpoints.auth import get_current_user
import requests

router = APIRouter(tags=["Pedidos"])


@router.post('/orders', status_code=status.HTTP_201_CREATED, response_model=OrderCreatedSchema, response_model_exclude_none=True)
@inject
async def create_order(request: Request, order_data: CreateOrderSchema, user_data_auth=Depends(get_current_user),
                       orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    order = await orders_service.create_order(order_data=order_data.dict(), 
                                              user_uuid_keycloak=user_data_auth.get('uuid'))
    if 'status' in order['payment_info'].keys():
        if order['payment_info']['status'] == 'error':
            return JSONResponse(content=order, status_code=400)
    return order

@router.post('/download', status_code=status.HTTP_200_OK)
def download(request: Request, billet_data: DownloadBillet):
    data = billet_data.dict()
    response = requests.get(data['url'])
    return StreamingResponse(io.BytesIO(response.content), media_type="application/pdf")

@router.post('/orders/calc')
@inject
async def calc_order(request: Request, order_data: CreateOrderSchema, user_data_auth=Depends(get_current_user),
                       orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    order = await orders_service.calc_order(order_data=order_data.dict())
    return order

@router.get('/orders/{order_uuid}', response_model=OrderReponse)
@inject
async def get_order_by_uuid(request: Request, order_uuid: str,
                            orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    order =  await orders_service.get_order_by_uuid(order_uuid=order_uuid)
    return order


@router.get('/orders')
@inject
async def get_orders(request: Request, user_data_auth=Depends(get_current_user),
                     orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    params = request.query_params
    params = {
        'expirate': bool(strtobool(params.get('expirate', 'False'))),
        'status': params.get('status', None),
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }
    orders = await orders_service.get_all_orders(params=params)
    return orders

@router.get('/order/user', response_model=OrdersPaginateSchema)
@inject
async def get_orders_by_user(request: Request, user_data_auth=Depends(get_current_user),
                             orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    params = request.query_params
    params = {
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }
    orders = await orders_service.get_orders_by_user(user_uuid=user_data_auth.get('uuid'), params=params)
    return orders
                                  


@router.patch('/orders/{order_uuid}/status', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_order_status(request: Request, order_uuid: str, update_status: UpdateStatusSchema, user_data_auth=Depends(get_current_user),
                              orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    await orders_service.update_order_status(order_uuid=order_uuid, status=update_status.status)
    return 


@router.post('/orders/webhook', status_code=status.HTTP_200_OK)
@inject
async def order_webhook(request: Request, orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    data = await request.json()
    if data.get('event') == 'PAYMENT_RECEIVED':
        await orders_service.check_and_update_orders(data=data)
        return
    return

@router.patch('/orders/{order_id}/products/decrement', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def decrement_product_quantity(request: Request, order_id: str,
                                        orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    await orders_service.decrement_products_quantity(order_id=order_id)
    return 

@router.get('/orders/{order_uuid}/products', status_code=status.HTTP_200_OK)
@inject
async def get_products_by_order_uuid(request: Request, order_uuid: str,
                                    orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    products = await orders_service.get_products_by_order_id(order_uuid=order_uuid)
    return products

@router.get('/menager/orders', status_code=status.HTTP_200_OK, response_model=OrdersPaginateSchema)
@inject
async def get_orders_by_menager(request: Request, limit: int = 12, offset: int = 0,
                                order_by: str = "created_at", order_type: str = "desc",
                                send_status: Union[str, None] = None,
                                start_date: Union[str, None] = None, end_date: Union[str, None] = None,
                                orders_service: OrdersService = Depends(Provide(Container.orders_service))):    
    params = {
        'limit': limit,
        'offset': offset,
        'start_date': start_date,
        'end_date': end_date,
        'order_by': order_by,
        'order_type': order_type,
        'send_status': send_status
    }

    orders_service = await orders_service.get_orders_by_menager(params=params)
    return orders_service


@router.patch('/menager/orders/{order_uuid}/status-send', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_order_status(request: Request, order_uuid: str, update_status: UpdateStatusSendoSchema,
                              orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    await orders_service.update_order_status_send(order_uuid=order_uuid, status_send=update_status.status_send)
    return 


@router.get('/orders/labels/{order_uuid}', status_code=status.HTTP_200_OK)
@inject
async def get_labels(request: Request, order_uuid: str, orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    labels = await orders_service.get_labels(order_uuid)
    return labels


def configure(app: FastAPI):
    app.include_router(router)
