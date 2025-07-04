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
        obj_in_data = obj_in.dict()
        # Create a new record in the database
        model = await self.model.create(**obj_in_data)
        return model

    async def update(self, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> bool:
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
            logger.warning("No hay datos para actualizar, retornando False")
            return False

        try:
            # Primero obtenemos el objeto existente para verificar que existe
            obj = await self.model.get_or_none(**{pk: id})
            if not obj:
                logger.warning(f"No se encontró el objeto con {pk}={id}")
                return False
                
            # Actualizamos solo los campos proporcionados
            updated_count = await self.model.filter(**{pk: id}).update(**update_data)
            logger.info(f"Registros actualizados: {updated_count}")
            return updated_count > 0
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
