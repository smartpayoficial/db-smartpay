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
        self, *, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = {}
    ) -> List[ModelType]:
        return await self.model.filter(**filters).all().offset(skip).limit(limit)

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = await self.model.create(**obj_in.dict())
        return db_obj

    async def update(self, *, id: Any, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        db_obj = await self.model.filter(pk=id).first()
        if not db_obj:
            return None
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db_obj.save()
        return db_obj

    async def delete(self, *, id: Any) -> Optional[ModelType]:
        db_obj = await self.model.filter(pk=id).first()
        if not db_obj:
            return None
        await db_obj.delete()
        return db_obj

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self.model.filter(**payload).all().count()
        return count
