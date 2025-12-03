from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.account_type import AccountType
from app.schemas.account_type import AccountTypeCreate, AccountTypeUpdate

from typing import List, Optional
from uuid import UUID

from tortoise.transactions import in_transaction

class CRUDAccountType(CRUDBase[AccountType, AccountTypeCreate, AccountTypeUpdate]):
    async def get_by_country_and_category(
        self,
        country_id: UUID,
        categories: Optional[List[str]] = None
    ) -> List[AccountType]:
        query = """
            SELECT DISTINCT at.id, at.name, at.description, at.icon_url, at.is_international, at.form_schema, at.category, at.created_at
            FROM account_types AS at
            LEFT JOIN country_account_types AS cat ON at.id = cat.account_type_id
            WHERE (at.is_international = TRUE OR cat.country_id = $1)
        """

        params = [country_id]

        if categories:
            # Use ANY() to filter by a list of categories. Pass the list as a single parameter.
            query += " AND at.category = ANY($2::account_category_enum[])"
            params.append(categories)

        query += " ORDER BY at.created_at DESC"

        async with in_transaction() as conn:
            results = await conn.execute_query_dict(query, params)

        return [self.model(**row) for row in results]


crud_account_type = CRUDAccountType(model=AccountType)
