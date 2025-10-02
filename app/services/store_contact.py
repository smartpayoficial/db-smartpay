from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
from fastapi import HTTPException

from app.infra.postgres.crud.store_contact import crud_store_contact
from app.services.base import BaseService
from app.schemas.store_contact import StoreContactCreate
from app.services.account_type import account_type_service
from app.infra.postgres.models.store_contact import StoreContact


def _generate_json_schema(form_schema: list) -> dict:
    properties = {}
    required = []
    for field in form_schema:
        field_name = field.get("name")
        if not field_name:
            continue

        field_type = field.get("type")
        # Default to string type for simplicity
        prop = {"type": "string"}

        if field_type == "number":
            prop["type"] = "number"
        elif field_type == "boolean":
            prop["type"] = "boolean"

        if field_type == "select" and "options" in field:
            enum_values = [opt.get("value") for opt in field["options"] if "value" in opt]
            if enum_values:
                prop["enum"] = enum_values

        properties[field_name] = prop

        if field.get("required"):
            required.append(field_name)

    schema = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
        
    return schema


class StoreContactService(BaseService):
    async def get_by_store_and_categories(self, store_id, categories=None):
        return await self.crud.get_by_store_and_categories(store_id, categories)
    async def get_all(self, *, skip: int = 0, limit: int = 100, payload=None, prefetch_fields=None, order_by=None) -> list:
        # Always order by created_at DESC unless overridden
        order = order_by if order_by else ["-created_at"]
        return await self.crud.get_all(skip=skip, limit=limit, payload=payload or {}, prefetch_fields=prefetch_fields, order_by=order)

    async def create(self, *, obj_in: StoreContactCreate) -> StoreContact:
        """
        Create a new store contact after validating contact_details against the
        account_type's form_schema.
        """
        account_type = await account_type_service.get(id=obj_in.account_type_id)
        if not account_type:
            raise HTTPException(status_code=404, detail="AccountType not found")

        try:
            validation_schema = _generate_json_schema(account_type.form_schema)
            validate(instance=obj_in.contact_details, schema=validation_schema)
        except SchemaError as e:
            raise HTTPException(status_code=500, detail=f"Invalid form schema definition in DB: {e.message}")
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=f"Invalid contact_details: {e.message}")

        return await self.crud.create(obj_in=obj_in)


store_contact_service = StoreContactService(crud=crud_store_contact)