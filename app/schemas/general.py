from typing import Any, TypeVar

from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Any)

CrudType = TypeVar("CrudType", bound=Any)

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
