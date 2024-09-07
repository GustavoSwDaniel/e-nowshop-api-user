from typing import Dict

from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.endpoints.metrics.repository import OrdersRepository, OrdersItemsRepository, UsersRepository



class MetricsService:
    def __init__(self, order_repository: OrdersRepository,
                 order_items_repository: OrdersItemsRepository,
                 users_repository: UsersRepository,):
        self.order_repository = order_repository
        self.order_items_repository = order_items_repository
        self.user_repository = users_repository

    async def get_metrics(self) -> Dict:
        total_orders = await self.order_repository.get_count_total_orders_approvad()
        total_value_orders = await self.order_repository.get_sum_total_value_orders_approvaded()
        total_users = await self.user_repository.get_count_total_users()
        total_sales_per_category = await self.order_items_repository.count_sales_per_category()
        orders_by_mouth = await self.order_repository.get_orders_by_mouth()
        orders_by_stete = await self.order_repository.get_orders_by_states()

        return {
            'metrics': {
                'total_orders': {'name' : 'Quantidade de pedidos', 'value': total_orders},
                'total_value_orders': {'name' : 'Valor total dos pedidos', 'value': f'R$ {total_value_orders / 100:.2f}'},
                'total_users': {'name' : 'Quantidade de usuários', 'value': total_users},
                'category_must_sold': {'name' : 'Categoria mais vendida', 'value': max(total_sales_per_category, key=total_sales_per_category.get)},
            },
            'charts': {
                'pie': 
                    [ 
                        {'name': 'Vendas por categoria', 'value' :total_sales_per_category},
                        {'name': 'Vendas por estado', 'value': orders_by_stete}
                    ]
                ,
                'bar': [
                        {'name': 'Vendas por mês', 'value' :orders_by_mouth}
                ]
            }
        }