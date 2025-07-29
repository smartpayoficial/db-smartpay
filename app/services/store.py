from typing import Any, Dict, List, Optional
from uuid import UUID

from app.infra.postgres.crud.store import crud_store
from app.infra.postgres.models.user import User
from app.schemas.store import StoreDB, StoreCreate, StoreUpdate
from app.services.base import BaseService


class StoreService(BaseService):
    async def get_with_country(self, *, id: UUID) -> Optional[StoreDB]:
        """
        Retrieve a single store by its ID with country information.
        """
        return await self.crud.get_with_country(id=id)
    
    async def get_all_with_country(self, *, skip: int = 0, limit: int = 100, payload: Dict[str, Any] = {}) -> List[StoreDB]:
        """
        Retrieve all stores with country information.
        """
        return await self.crud.get_all_with_country(skip=skip, limit=limit, payload=payload)

    async def create(self, *, obj_in: StoreCreate, admin_id: Optional[UUID] = None) -> StoreDB:
        """Crea una nueva tienda y carga sus relaciones.
        
        Args:
            obj_in: Datos de la tienda a crear (StoreCreate o dict)
            admin_id: ID del administrador (opcional)
            
        Returns:
            StoreDB: Tienda creada con sus relaciones
        """
        # Asegurarnos de trabajar siempre con un modelo Pydantic
        if not hasattr(obj_in, "dict"):
            # Si llega un diccionario lo validamos/convertimos
            obj_in = StoreCreate(**obj_in)

        # Si se proporciona admin_id, actualizamos el modelo sin mutarlo en sitio
        if admin_id is not None:
            obj_in = obj_in.copy(update={"admin_id": admin_id})

        # Crear la tienda (el CRUD aceptará el modelo Pydantic directamente)
        store = await self.crud.create(obj_in=obj_in)

        # Convertir el modelo Tortoise a Pydantic antes de retornar
        if store:
            return StoreDB.from_orm(store)
        return None

    async def update(self, *, id: UUID, obj_in: StoreUpdate, admin_id: Optional[UUID] = None) -> StoreDB:
        """Actualiza una tienda existente y carga sus relaciones.
        
        Args:
            id: ID de la tienda a actualizar
            obj_in: Datos de actualización (StoreUpdate o dict)
            admin_id: ID del administrador (opcional)
            
        Returns:
            StoreDB: Tienda actualizada con sus relaciones
        """
        # Manejar tanto objetos Pydantic como diccionarios
        if hasattr(obj_in, 'dict'):
            store_data = obj_in.dict(exclude_unset=True, exclude_none=True)
        else:
            # Si es un diccionario, validarlo con Pydantic
            store_data = StoreUpdate(**obj_in).dict(exclude_unset=True, exclude_none=True)
        
        # Si se proporciona admin_id, asegurarse de que se use
        if admin_id:
            store_data['admin_id'] = admin_id
        
        # Actualizar la tienda (el método update en CRUDBase ahora devuelve el objeto actualizado)
        updated_store = await self.crud.update(id=id, obj_in=store_data)
        
        # Convertir el modelo Tortoise a Pydantic
        if updated_store:
            return StoreDB.from_orm(updated_store)
        return None

    async def delete(self, *, id: UUID) -> bool:
        """Delete a store after disassociating all users from it.
        
        Args:
            id: UUID of the store to delete
            
        Returns:
            bool: True if the store was deleted, False otherwise
        """
        # First, disassociate all users from this store
        # Using store_id=None directly instead of store=None
        await User.filter(store_id=id).update(store_id=None)
        
        # Then delete the store
        return await super().delete(id=id)


store_service = StoreService(crud=crud_store)
