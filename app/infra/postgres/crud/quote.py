from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.quote import Quote
from app.schemas.quote import CreateQuote, UpdateQuote


class CRUDQuote(CRUDBase[Quote, CreateQuote, UpdateQuote]):
    ...
    """
    Basic CRUD of the Quote model, inherits crud base methods
    """


crud_quote = CRUDQuote(model=Quote)
