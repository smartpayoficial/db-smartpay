from typing import List, Optional
from uuid import UUID
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from app.infra.postgres.models.action import ActionState
from app.schemas.action import ActionCreate, ActionResponse, ActionUpdate
from app.services.action import action_service

router = APIRouter()


@router.get("", response_model=List[ActionResponse], response_class=JSONResponse)
async def get_all_actions(
    device_id: Optional[UUID] = None,
    state: Optional[ActionState] = None,
    skip: int = 0,
    limit: int = 100,
):
    filters = {}
    if device_id:
        filters["device_id"] = device_id
    if state:
        filters["state"] = state

    return await action_service.get_all(skip=skip, limit=limit, filters=filters)

@router.post("", response_model=ActionResponse, response_class=JSONResponse, status_code=201)
async def create_action(new_action: ActionCreate):
    return await action_service.create(obj_in=new_action)

@router.get("/{action_id}", response_model=ActionResponse, response_class=JSONResponse)
async def get_action_by_id(action_id: UUID = Path(...)):
    action = await action_service.get_by_id(action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action

@router.patch("/{action_id}", response_model=ActionResponse, response_class=JSONResponse)
async def update_action(action_id: UUID, update: ActionUpdate):
    action = await action_service.update(action_id, obj_in=update)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action

@router.delete("/{action_id}", response_class=JSONResponse)
async def delete_action(action_id: UUID):
    deleted = await action_service.delete(action_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"deleted": True}
