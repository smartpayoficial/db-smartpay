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
        filters: Dict[str, Any] = {},
        prefetch_fields: Optional[List[str]] = None,
    ) -> List[ModelType]:
        query = self.model.filter(**filters)
        if prefetch_fields:
            query = query.prefetch_related(*prefetch_fields)
        return await query.offset(skip).limit(limit).all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        # Create a new record in the database
        model = await self.model.create(**obj_in_data)
        return model

    async def update(self, *, id: Any, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> bool:
        pk = self.model._meta.pk_attr
        update_data = (
            obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        )

        if not update_data:
            # If there's nothing to update, just check for existence.
            return await self.model.filter(**{pk: id}).exists()

        updated_count = await self.model.filter(**{pk: id}).update(**update_data)

        return updated_count > 0

    async def delete(self, *, id: Any) -> int:
        pk = self.model._meta.pk_attr
        deleted_count = await self.model.filter(**{pk: id}).delete()
        return deleted_count

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self.model.filter(**payload).all().count()
        return count
