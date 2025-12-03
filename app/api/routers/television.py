from typing import List, Optional, Dict
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse, Response

from app.schemas.television import TelevisionCreate, TelevisionDB, TelevisionUpdate

from app.schemas.general import CountResponse
from app.services.television import television_service

# Television Router
router = APIRouter()

@router.get(
    "/",
    response_class=JSONResponse,
    response_model=List[TelevisionDB],
    status_code=200,
)
async def get_all_televisions(
    enrolment_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    store_id: Optional[UUID] = Query(None, description="Filter televisions by store_id of the user")
):
    import sys
    
    # Debug log for parameters
    if store_id:
        print(f"DEBUG: get_all_televisions called with store_id={store_id}", file=sys.stderr)
    
    try:
        # Construir payload para el servicio
        payload = {}
        if enrolment_id:
            payload["enrolment_id"] = enrolment_id
        if user_id:
            payload["user_id"] = user_id
        
        # Obtener dispositivos a través del servicio
        televisions = await television_service.get_all(payload=payload)
        
        # Si se proporciona store_id, filtrar los dispositivos donde el usuario en el enrollment pertenece a la tienda especificada
        if store_id:
            print(f"DEBUG: Filtering televisions for store_id={store_id}", file=sys.stderr)
            filtered_televisions = []
            for television in televisions:
                # Verificar si el dispositivo tiene un enrollment con usuario o vendedor asociado a la tienda
                if television.enrolment and (
                    (television.enrolment.user and television.enrolment.user.store_id == store_id) or
                    (television.enrolment.vendor and television.enrolment.vendor.store_id == store_id)
                ):
                    filtered_televisions.append(television)
            
            # Debug output
            print(f"DEBUG: Filtered - Found {len(filtered_televisions)} devices for store_id={store_id}", file=sys.stderr)
            return filtered_televisions
        
        return televisions
    except Exception as e:
        print(f"ERROR: Exception in get_all_televisions: {str(e)}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving televisions: {str(e)}"
        )


@router.post(
    "/",
    response_class=JSONResponse,
    response_model=TelevisionDB,
    status_code=201,
)
async def create_television(new_television: TelevisionCreate):
    television = await television_service.create(obj_in=new_television)
    return television


@router.get(
    "/count",
    response_class=JSONResponse,
    response_model=CountResponse,
    status_code=200,
)
async def count_televisions():
    """
    Count the total number of devices in the system.
    
    Returns:
        CountResponse: Object containing the total count of devices
    """
    count = await television_service.count()
    return {"count": count}


@router.get(
    "/{television_id}",
    response_class=JSONResponse,
    response_model=TelevisionDB,
    status_code=200,
)
async def get_television_by_id(television_id: UUID = Path(...)):
    television = await television_service.get(id=television_id)
    if television is None:
        raise HTTPException(status_code=404, detail="Television not found")
    return television


@router.patch(
    "/{television_id}",
    response_class=JSONResponse,
    response_model=TelevisionDB,
    status_code=200,
)
async def update_television(update_television: TelevisionUpdate, television_id: UUID = Path(...)):
    updated = await television_service.update(id=television_id, obj_in=update_television)
    if not updated:
        raise HTTPException(status_code=404, detail="Television not found")
    
    television = await television_service.get(id=television_id)
    return television


@router.delete(
    "/{television_id}",
    response_class=Response,
    status_code=204,
)
async def delete_television(television_id: UUID = Path(...)):
    deleted = await television_service.delete(id=television_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Television not found")
