from typing import Any, Dict, List, Optional, TypeVar

from app.schemas.general import CreateSchemaType, CrudType, UpdateSchemaType

IdType = TypeVar("IdType")


class BaseService:
    def __init__(self, *, crud: CrudType) -> None:
        self._crud = crud

    async def create(self, *, obj_in: CreateSchemaType) -> Dict[str, Any]:
        obj_db = await self._crud.create(obj_in=obj_in)
        return obj_db

    async def update(self, *, id: IdType, obj_in: UpdateSchemaType) -> bool:
        status = await self._crud.update(_id=id, obj_in=obj_in)
        return status

    async def get_all(
        self, *, skip: int = 0, limit: int = 10, payload: Dict[str, Any] = {}
    ) -> List[Dict[str, Any]]:
        objs_db = await self._crud.get_all(payload=payload, skip=skip, limit=limit)
        return objs_db

    async def get_by_id(self, *, id: IdType) -> Optional[Dict[str, Any]]:
        obj_db = await self._crud.get_by_id(_id=id)
        return obj_db

    async def delete(self, *, id: IdType) -> int:
        deletes = await self._crud.delete(_id=id)
        return deletes

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self._crud.count(payload=payload)
        return count
