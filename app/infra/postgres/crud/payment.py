from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.payment import Payment
from app.schemas.payment import PaymentCreate

# Si tienes un PaymentUpdate, impórtalo aquí. Si no, puedes crear uno vacío o manejar solo PaymentCreate.
try:
    from app.schemas.payment import PaymentUpdate
except ImportError:
    PaymentUpdate = None  # O define una clase vacía si es necesario

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    pass

crud_payment = CRUDPayment(model=Payment)
