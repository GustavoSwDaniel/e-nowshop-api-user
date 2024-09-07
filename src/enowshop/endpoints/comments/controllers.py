from fastapi import APIRouter, Depends, FastAPI, Request
from enowshop.endpoints.comments.service import CommentService
from enowshop.endpoints.comments.schema import PaginateCommentsSchema, RegisterComment
from dependency_injector.wiring import inject, Provide

from enowshop.infrastructure.containers import Container
from enowshop.endpoints.auth import get_current_user


router = APIRouter(tags=["Comments"])


@router.post("/comments" )
@inject
async def create_comments(request: Request, data: RegisterComment, user_data_auth=Depends(get_current_user),
                     comment_service: CommentService = Depends(Provide[Container.comment_service])):
    return await comment_service.register_comments(data.dict(), user_data_auth)

@router.get("/comments/{product_id}", response_model=PaginateCommentsSchema)
@inject
async def get_comments(request: Request, product_id:int, comment_service: CommentService = Depends(Provide[Container.comment_service])):
    params = request.query_params
    params = {
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }
    
    comments =  await comment_service.get_comments(params=params, product_id=product_id)
    return comments

def configure(app: FastAPI):
    app.include_router(router)