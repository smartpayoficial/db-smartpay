from typing import Any, Dict, List, Optional
from uuid import UUID

from app.infra.postgres.crud.store import crud_store
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
        # Manejar tanto objetos Pydantic como diccionarios
        if hasattr(obj_in, 'dict'):
            store_data = obj_in.dict()
        else:
            # Si es un diccionario, validarlo con Pydantic
            store_data = StoreCreate(**obj_in).dict()
        
        if 'admin_id' in store_data and store_data['admin_id'] is None:
            del store_data['admin_id']
        store_data['admin_id'] = admin_id
        
        # Crear la tienda (el método create en CRUDBase ya carga las relaciones)
        store = await self.crud.create(obj_in=store_data)
        
        # Convertir el modelo Tortoise a Pydantic
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

store_service = StoreService(crud=crud_store)
