from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.store_contact import StoreContact
from app.schemas.store_contact import StoreContactCreate, StoreContactUpdate


class CRUDStoreContact(CRUDBase[StoreContact, StoreContactCreate, StoreContactUpdate]):
    async def get_by_store_and_categories(self, store_id, categories=None):
        """
        Obtiene los store_contacts filtrados por store_id y categorías.
        Usa un query específico para asegurar que el filtro por categoría funcione.
        """
        from tortoise.transactions import in_transaction

        # Query base que selecciona todos los campos necesarios
        query = """
            WITH filtered_contacts AS (
                SELECT 
                    sc.id,
                    sc.store_id,
                    sc.account_type_id,
                    sc.contact_details,
                    sc.description,
                    sc.created_at,
                    sc.updated_at,
                    sc.deleted_at,
                    at.category
                FROM store_contact sc
                INNER JOIN account_types at ON sc.account_type_id = at.id
                WHERE sc.store_id = $1
                AND sc.deleted_at IS NULL
        """
        
        params = [str(store_id)]

        if categories:
            # Si hay categorías, agregamos el filtro
            query += " AND at.category = ANY($2::text[])"
            params.append(categories)

        # Cerramos el CTE y seleccionamos los resultados
        query += """
            )
            SELECT * FROM filtered_contacts
            ORDER BY created_at DESC
        """

        async with in_transaction() as conn:
            results = await conn.execute_query_dict(query, params)
            
        return [self.model(**row) for row in results]


crud_store_contact = CRUDStoreContact(model=StoreContact)
