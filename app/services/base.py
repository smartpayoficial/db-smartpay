from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError

from app.infra.postgres.crud.base import CRUDBase

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, crud: CRUDBase):
        self.crud = crud

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        payload: Optional[Dict[str, Any]] = None,
        prefetch_fields: Optional[List[str]] = None,
    ) -> List[ModelType]:
        # Parámetros básicos que todas las implementaciones de CRUD aceptan
        base_params = {"skip": skip, "limit": limit}
        if prefetch_fields:
            base_params["prefetch_fields"] = prefetch_fields
            
        # Si no hay filtros, simplemente llamamos al método con los parámetros básicos
        if payload is None:
            return await self.crud.get_all(**base_params)
            
        # Intentamos primero con el parámetro 'filters'
        try:
            filters_params = base_params.copy()
            filters_params["filters"] = payload
            return await self.crud.get_all(**filters_params)
        except TypeError:
            # Si falla, intentamos con el parámetro 'payload'
            try:
                payload_params = base_params.copy()
                payload_params["payload"] = payload
                return await self.crud.get_all(**payload_params)
            except TypeError:
                # Si ambos fallan, intentamos pasar los filtros directamente
                direct_params = base_params.copy()
                direct_params.update(payload)
                return await self.crud.get_all(**direct_params)

    async def get(self, id: Any) -> Optional[ModelType]:
        return await self.crud.get(id=id)

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        try:
            return await self.crud.create(obj_in=obj_in)
        except IntegrityError as e:
            error_message = str(e).lower()
            if "violates foreign key constraint" in error_message:
                # This is a generic FK error. More specific ones can be added if needed.
                raise HTTPException(status_code=400, detail="Referencia a entidad relacionada no válida.")
            elif "unique constraint" in error_message or "duplicate key" in error_message:
                if "enrolment_id" in error_message:
                    raise HTTPException(status_code=409, detail="Este código de enrollamiento ya existe.")
                elif "imei" in error_message:
                    raise HTTPException(status_code=409, detail="Ya existe un dispositivo con este IMEI.")
                elif "dni" in error_message:
                    raise HTTPException(status_code=409, detail="Ya existe un usuario con este DNI.")
                elif "email" in error_message:
                    raise HTTPException(status_code=409, detail="Ya existe un usuario con este email.")
                else:
                    raise HTTPException(status_code=409, detail="El recurso ya existe. Uno de los campos únicos está duplicado.")
            else:
                # Catch-all for other integrity errors
                raise HTTPException(status_code=500, detail=f"Error de integridad de datos: {error_message}")

    async def update(self, *, id: Any, obj_in: UpdateSchemaType) -> ModelType:
        return await self.crud.update(id=id, obj_in=obj_in)

    async def delete(self, *, id: Any) -> bool:
        return await self.crud.delete(id=id)
