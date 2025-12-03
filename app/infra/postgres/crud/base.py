from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from app.schemas.general import CreateSchemaType, ModelType, UpdateSchemaType

IdType = TypeVar("IdType")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):  # type: ignore
    def __init__(self, *, model: Type[ModelType]) -> None:
        self.model = model
        # Get the primary key field name from the model
        self.pk_field = next(
            field_name
            for field_name, field in model._meta.fields_map.items()
            if field.pk
        )

    async def get(self, *, id: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by its primary key.
        """
        pk = self.pk_field
        return await self.model.get_or_none(**{pk: id})

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        payload: Dict[str, Any] = {},
        prefetch_fields: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
    ) -> List[ModelType]:
        query = self.model.filter(**payload)
        if prefetch_fields:
            query = query.prefetch_related(*prefetch_fields)

        # Apply ordering
        if order_by:
            query = query.order_by(*order_by)
        elif hasattr(self.model, "created_at"):
            query = query.order_by("-created_at")
        elif hasattr(self.model, "initial_date"):
            query = query.order_by("-initial_date")

        return await query.offset(skip).limit(limit).all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        # Manejar tanto objetos Pydantic como diccionarios
        if hasattr(obj_in, 'dict'):
            obj_in_data = obj_in.dict()
        else:
            # Si es un diccionario, usarlo directamente
            obj_in_data = obj_in
        
        # Create a new record in the database
        model = await self.model.create(**obj_in_data)
        
        # Recargar el modelo con sus relaciones utilizando la clave primaria dinámica
        pk = self.pk_field
        model = await self.model.get(**{pk: getattr(model, pk)}).prefetch_related(*self.model._meta.fetch_fields)
        return model

    async def update(self, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        import logging
        logger = logging.getLogger(__name__)
        
        pk = self.pk_field
        logger.info(f"Actualizando modelo {self.model.__name__} con pk={pk}, id={id}")
        
        # Obtenemos solo los campos que se han establecido explícitamente
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_none=True)
        )
        
        logger.info(f"Datos de actualización: {update_data}")

        if not update_data:
            logger.warning("No hay datos para actualizar, retornando objeto original")
            # Devolvemos el objeto original sin cambios pero con sus relaciones
            return await self.model.get(**{pk: id}).prefetch_related(*self.model._meta.fetch_fields)

        try:
            # Primero obtenemos el objeto existente para verificar que existe
            obj = await self.model.get_or_none(**{pk: id})
            if not obj:
                logger.warning(f"No se encontró el objeto con {pk}={id}")
                return None
                
            # Manejo especial para claves foráneas para asegurar la actualización correcta
            from app.infra.postgres.models import Store # Importación local para evitar dependencias circulares
            if 'store_id' in update_data:
                store_id = update_data.pop('store_id') # Quitamos store_id para manejarlo por separado
                if store_id:
                    store_obj = await Store.get_or_none(id=store_id)
                    if not store_obj:
                        raise HTTPException(status_code=404, detail=f"Store con id {store_id} no encontrada.")
                    obj.store = store_obj
                else:
                    obj.store = None # Permitir desasociar la tienda

            # Actualizamos los campos restantes
            for field, value in update_data.items():
                setattr(obj, field, value)
            
            # Guardamos el objeto. Tortoise se encargará de las relaciones.
            await obj.save()
            logger.info(f"Objeto con {pk}={id} actualizado con los campos: {list(update_data.keys())}")

            # Devolvemos el objeto actualizado con sus relaciones
            await obj.fetch_related(*self.model._meta.fetch_fields)
            return obj
        except Exception as e:
            logger.error(f"Error al actualizar: {str(e)}")
            raise

    async def delete(self, *, id: Any) -> bool:
        pk = self.pk_field
        deleted_count = await self.model.filter(**{pk: id}).delete()
        return deleted_count > 0

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self.model.filter(**payload).all().count()
        return count
