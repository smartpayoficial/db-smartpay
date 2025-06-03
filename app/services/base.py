from typing import Any, Dict, List, Optional, TypeVar

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError

from app.schemas.general import CreateSchemaType, CrudType, UpdateSchemaType

IdType = TypeVar("IdType")


class BaseService:
    def __init__(self, *, crud: CrudType) -> None:
        self._crud = crud

    async def create(self, *, obj_in: CreateSchemaType) -> Dict[str, Any]:
        try:
            obj_db = await self._crud.create(obj_in=obj_in)
            return obj_db
        except IntegrityError as e:
            error_message = str(e)

            # Manejar violaciones de clave foránea
            if "violates foreign key constraint" in error_message:
                # Extraer información específica del error
                if "user_city_id_fkey" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de ciudad especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "city_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de ciudad especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "region_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de región especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "country_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de país especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "user_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de usuario especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "vendor_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de vendor especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "enrolment_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de enrollamiento especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "device_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de dispositivo especificado no existe. Verifica que sea un ID válido.",
                    )
                else:
                    # Error de clave foránea genérico
                    raise HTTPException(
                        status_code=400,
                        detail="Referencia inválida. Uno de los IDs especificados no existe en la base de datos.",
                    )

            # Manejar violaciones de restricción única
            elif (
                "unique constraint" in error_message or "duplicate key" in error_message
            ):
                if (
                    "enrolment_id" in error_message
                    or "device_enrolment_id" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Este código de enrollamiento ya ha sido utilizado para registrar un dispositivo.",
                    )
                elif "imei" in error_message or "device_imei" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un dispositivo registrado con este IMEI.",
                    )
                elif "dni" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un usuario registrado con este DNI.",
                    )
                elif "email" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un usuario registrado con este email.",
                    )
                else:
                    # Error de unicidad genérico
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un registro con estos datos. Verifica los campos únicos.",
                    )

            # Otros errores de integridad
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error de integridad de datos: {error_message}",
                )

    async def update(self, *, id: IdType, obj_in: UpdateSchemaType) -> bool:
        try:
            status = await self._crud.update(_id=id, obj_in=obj_in)
            return status
        except IntegrityError as e:
            error_message = str(e)

            # Manejar violaciones de clave foránea
            if "violates foreign key constraint" in error_message:
                if (
                    "city_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de ciudad especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "region_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de región especificado no existe. Verifica que sea un ID válido.",
                    )
                elif (
                    "country_id" in error_message
                    and "not present in table" in error_message
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="El ID de país especificado no existe. Verifica que sea un ID válido.",
                    )
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Referencia inválida. Uno de los IDs especificados no existe en la base de datos.",
                    )

            # Manejar violaciones de restricción única
            elif (
                "unique constraint" in error_message or "duplicate key" in error_message
            ):
                if "imei" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un dispositivo registrado con este IMEI.",
                    )
                elif "dni" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un usuario registrado con este DNI.",
                    )
                elif "email" in error_message:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un usuario registrado con este email.",
                    )
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Ya existe un registro con estos datos. Verifica los campos únicos.",
                    )

            # Otros errores de integridad
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error de integridad de datos: {error_message}",
                )

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
