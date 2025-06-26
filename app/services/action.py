from uuid import UUID
from typing import List, Optional
from app.infra.postgres.models.action import Action
from app.schemas.action import ActionCreate, ActionUpdate

class ActionService:
    async def get_all(self) -> List[Action]:
        return await Action.all()

    async def get_by_id(self, action_id: UUID) -> Optional[Action]:
        return await Action.filter(action_id=action_id).first()

    async def create(self, obj_in: ActionCreate) -> Action:
        data = obj_in.dict()
        data['device_id'] = str(data.pop('device_id'))
        data['applied_by_id'] = str(data.pop('applied_by_id'))
        action = await Action.create(**data)
        return action

    async def update(self, action_id: UUID, obj_in: ActionUpdate) -> Optional[Action]:
        action = await self.get_by_id(action_id)
        if not action:
            return None
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(action, field, value)
        await action.save()
        return action

    async def delete(self, action_id: UUID) -> bool:
        action = await self.get_by_id(action_id)
        if not action:
            return False
        await action.delete()
        return True

action_service = ActionService()
