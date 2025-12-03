from typing import List, Optional
from uuid import UUID
from tortoise.transactions import in_transaction
from app.infra.postgres.crud.account_type import crud_account_type
from app.infra.postgres.models.account_type import AccountType
from app.infra.postgres.models.country import Country
from app.services.base import BaseService

class AccountTypeService(BaseService):
    async def get_for_country(self, *, country_id: UUID) -> List[AccountType]:
        """
        Gets all account types available for a specific country, including
        international ones.
        """
        country_specific_types = []
        country = await Country.get_or_none(country_id=country_id)

        if country:
            async with in_transaction() as conn:
                query = 'SELECT "account_type_id" FROM "country_account_types" WHERE "country_id" = $1'
                account_type_ids_result = await conn.execute_query_dict(query, [country_id])
                account_type_ids = [row['account_type_id'] for row in account_type_ids_result]

            if account_type_ids:
                country_specific_types = await self.crud.model.filter(id__in=account_type_ids)

        international_types = await self.crud.model.filter(is_international=True)

        combined_types = {at.id: at for at in country_specific_types}
        for at in international_types:
            combined_types[at.id] = at

        return list(combined_types.values())

    async def get_account_types(
        self, *, country_id: Optional[UUID] = None, categories: Optional[List[str]] = None
    ) -> List[AccountType]:
        """
        Gets all account types based on filters.
        """
        # Si se filtra por país o categorías, usa el método raw SQL del CRUD
        if country_id or categories:
            return await self.crud.get_by_country_and_category(
                country_id=country_id or UUID(int=0),
                categories=categories
            )
        # Si no hay filtros, retorna todos
        # Always order by created_at DESC unless overridden
        return await self.crud.model.all().order_by("-created_at").prefetch_related("countries")

account_type_service = AccountTypeService(crud=crud_account_type)