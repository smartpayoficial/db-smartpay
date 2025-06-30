from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

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

    async def get(self, *, id: IdType) -> Optional[ModelType]:
        """
        Retrieve a single record by its primary key.
        """
        if id:
            filter_kwargs = {self.pk_field: id}
            return await self.model.filter(**filter_kwargs).first()
        return None

    async def get_all(
        self, *, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = {}
    ) -> List[ModelType]:
        return await self.model.filter(**filters).all().offset(skip).limit(limit)

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.dict()
        # Create a new record in the database
        model = await self.model.create(**obj_in_data)
        return model

    async def update(self, *, id: IdType, obj_in: UpdateSchemaType) -> bool:
        filter_kwargs = {self.pk_field: id}
        model = await self.model.get_or_none(**filter_kwargs)
        if not model:
            return False

        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)

        await model.save()
        return True

    async def delete(self, *, id: IdType) -> int:
        filter_kwargs = {self.pk_field: id}
        deleted_count = await self.model.filter(**filter_kwargs).delete()
        return deleted_count

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self.model.filter(**payload).all().count()
        return count
