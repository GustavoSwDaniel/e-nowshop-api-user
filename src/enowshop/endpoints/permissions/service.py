import uuid
from enowshop.endpoints.permissions.repository import PermissionsRepository




class PermissionsService:
    def __init__(self, permissions_repository: PermissionsRepository) -> None:
        self.permissions_repository = permissions_repository
    
    async def create_permission(self, data):
        data['uuid'] = str(uuid.uuid4())
        return await self.permissions_repository.create(data)
    
    async def get_permissions(self):
        permissions = await self.permissions_repository.get_all()
        return permissions
        
    

   