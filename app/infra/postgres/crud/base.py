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

    async def get_all(
        self,
        *,
        payload: Dict[str, Any] = {},
        skip: int = 0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        query = self.model.filter(**payload) if payload else self.model
        model = await query.all().offset(skip).limit(limit).values()
        return model

    async def create(self, *, obj_in: CreateSchemaType) -> Dict[str, Any]:
        obj_in_data = obj_in.dict()
        model = self.model(**obj_in_data)
        await model.save()
        return await model.values()

    async def update(self, *, _id: IdType, obj_in: UpdateSchemaType) -> bool:
        filter_kwargs = {self.pk_field: _id}
        model = await self.model.get(**filter_kwargs)
        if not model:
            return False

        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)

        await model.save()
        return True

    async def delete(self, *, _id: IdType) -> int:
        filter_kwargs = {self.pk_field: _id}
        deletes = await self.model.filter(**filter_kwargs).first().delete()
        return deletes

    async def get_by_id(self, *, _id: IdType) -> Optional[Dict[str, Any]]:
        if _id:
            filter_kwargs = {self.pk_field: _id}
            model = await self.model.filter(**filter_kwargs).first().values()
            if model:
                return model[0] if isinstance(model, list) else model
        return None

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self.model.filter(**payload).all().count()
        return count
