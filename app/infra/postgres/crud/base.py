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
        pk = self.model._meta.pk_attr
        return await self.model.get_or_none(**{pk: id})

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        payload: Dict[str, Any] = {},
        prefetch_fields: Optional[List[str]] = None,
    ) -> List[ModelType]:
        query = self.model.filter(**payload)
        if prefetch_fields:
            query = query.prefetch_related(*prefetch_fields)
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
        
        # Asegurar que el modelo se carga con sus relaciones
        if hasattr(model, 'id'):
            # Recargar el modelo con sus relaciones
            model = await self.model.get(id=model.id).prefetch_related(*self.model._meta.fetch_fields)
        
        return model

    async def update(self, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        import logging
        logger = logging.getLogger(__name__)
        
        pk = self.model._meta.pk_attr
        logger.info(f"Actualizando modelo {self.model.__name__} con pk={pk}, id={id}")
        
        # Obtenemos solo los campos que se han establecido explícitamente
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True, exclude_none=True)
        )
        
        logger.info(f"Datos de actualización: {update_data}")

        if not update_data:
            logger.warning("No hay datos para actualizar, retornando objeto original")
            # Devolvemos el objeto original sin cambios pero con sus relaciones
            return await self.model.get(id=id).prefetch_related(*self.model._meta.fetch_fields)

        try:
            # Primero obtenemos el objeto existente para verificar que existe
            obj = await self.model.get_or_none(**{pk: id})
            if not obj:
                logger.warning(f"No se encontró el objeto con {pk}={id}")
                return None
                
            # Actualizamos solo los campos proporcionados
            updated_count = await self.model.filter(**{pk: id}).update(**update_data)
            logger.info(f"Registros actualizados: {updated_count}")
            
            if updated_count > 0:
                # Devolvemos el objeto actualizado con sus relaciones
                return await self.model.get(id=id).prefetch_related(*self.model._meta.fetch_fields)
            else:
                # Si no se actualizó nada, devolvemos el objeto original
                return obj
        except Exception as e:
            logger.error(f"Error al actualizar: {str(e)}")
            raise

    async def delete(self, *, id: Any) -> bool:
        pk = self.model._meta.pk_attr
        deleted_count = await self.model.filter(**{pk: id}).delete()
        return deleted_count > 0

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self.model.filter(**payload).all().count()
        return count
