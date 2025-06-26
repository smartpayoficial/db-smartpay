from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from app.schemas.action import ActionCreate, ActionUpdate, ActionResponse
from app.services.action import action_service

router = APIRouter()

@router.get("", response_model=List[ActionResponse], response_class=JSONResponse)
async def get_all_actions():
    return await action_service.get_all()

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
