from typing import Any, Dict, List, Optional

from app.schemas.general import CreateSchemaType, CrudType, UpdateSchemaType


class BaseService:
    def __init__(self, *, crud: CrudType) -> None:
        self._crud = crud

    async def create(self, *, obj_in: CreateSchemaType) -> Dict[str, Any]:
        obj_db = await self._crud.create(obj_in=obj_in)
        return obj_db

    async def update(self, *, _id: int, obj_in: UpdateSchemaType) -> bool:
        status = await self._crud.update(_id=_id, obj_in=obj_in)
        return status

    async def get_all(
        self, *, skip: int, limit: int, payload: Dict[str, Any] = {}
    ) -> List[Dict[str, Any]]:
        objs_db = await self._crud.get_all(payload=payload, skip=skip, limit=limit)
        return objs_db

    async def get_by_id(self, *, _id: int) -> Optional[Dict[str, Any]]:
        obj_db = await self._crud.get_by_id(_id=_id)
        return obj_db

    async def delete(self, *, _id: int) -> int:
        deletes = await self._crud.delete(_id=_id)
        return deletes

    async def count(self, *, payload: Dict[str, Any] = {}) -> int:
        count = await self._crud.count(payload=payload)
        return count
