
from datetime import datetime
from typing import Dict
from enowshop.endpoints.comments.repository import CommentsRepository
from enowshop.endpoints.paginate import paginate
from enowshop.endpoints.users.repository import UsersRepository
from enowshop.endpoints.orders.repository import OrderItemsRepository

class CommentService:
    def __init__(self, comments_repository: CommentsRepository, user_repository: UsersRepository, order_items_repository: OrderItemsRepository):
        self.comments_repository = comments_repository
        self.user_reponsitory = user_repository
        self.order_items_repository = order_items_repository

    async def register_comments(self, comment, user_data):
        user  = await self.user_reponsitory.filter_by({"uuid": user_data['uuid']})
        comment['user_id'] = user.id
        await self.comments_repository.create(comment)
        await self.order_items_repository.update_by_product_id(
            pk=comment['product_id'], values={'is_rated': True})
    
    async def get_comments(self, params: Dict, product_id: int):
        results, total = await self.comments_repository.get_all_comments_paginated(params=params, product_id=product_id)
        return paginate(results, params.get('offset'), total)