from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.infra.postgres.models import User
from app.infra.postgres.models.account_type import AccountCategoryEnum
from app.schemas.store_contact import (
    StoreContactCreate, StoreContactDB, StoreContactUpdate
)
from app.services.store_contact import store_contact_service
from app.services.store import store_service
from app.services.account_type import account_type_service

router = APIRouter()


@router.get(
    "/by-store/{store_id}",
    response_model=List[StoreContactDB],
    summary="Get All Contacts for a Store",
)
async def get_contacts_for_store(
        store_id: UUID,
        categories: Optional[List[AccountCategoryEnum]] = None,
    ):
    """
    Get all payment method contacts for a specific store.

    - Si **categories** se provee, filtra los contactos por las categorías especificadas.
    - Puedes enviar varias categorías usando: `?categories=CONTACT&categories=BANK`
    - Si no se envía, retorna todos los contactos del store.
    """
    if categories:
        # Convertimos las categorías a una lista de strings para el filtro SQL
        category_values = [cat.value for cat in categories]
        contacts = await store_contact_service.get_by_store_and_categories(
            store_id=store_id,
            categories=category_values
        )
    else:
        contacts = await store_contact_service.get_all(
            payload={"store_id": store_id}, prefetch_fields=["account_type"]
        )
    return contacts


@router.post(
    "/",
    response_model=StoreContactDB,
    status_code=201,
    summary="Create a new Store Contact"
)
async def create_store_contact(
    contact_in: StoreContactCreate,
):
    """Create a new payment method contact for a store."""
    store = await store_service.get(id=contact_in.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    await store.fetch_related("country")
    country_id = store.country.country_id
    
    valid_account_types = await account_type_service.get_for_country(country_id=country_id)
    valid_account_type_ids = [at.id for at in valid_account_types]

    if contact_in.account_type_id not in valid_account_type_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Account type {contact_in.account_type_id} is not valid for the store's country."
        )

    contact = await store_contact_service.create(obj_in=contact_in)
    return contact


@router.put(
    "/{contact_id}",
    response_model=StoreContactDB,
    summary="Update a Store Contact"
)
async def update_store_contact(
    contact_id: UUID,
    contact_in: StoreContactUpdate,
):
    """Update a store's payment method contact."""
    existing_contact = await store_contact_service.get(id=contact_id)
    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact = await store_contact_service.update(id=contact_id, obj_in=contact_in)
    return contact


@router.delete(
    "/{contact_id}",
    status_code=204,
    summary="Delete a Store Contact"
)
async def delete_store_contact(
    contact_id: UUID,
):
    """Delete a store's payment method contact."""
    existing_contact = await store_contact_service.get(id=contact_id)
    if not existing_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    await store_contact_service.delete(id=contact_id)
    return