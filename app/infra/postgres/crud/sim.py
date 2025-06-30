from app.infra.postgres.crud.base import CRUDBase
from app.infra.postgres.models.sim import Sim
from app.schemas.sim import SimCreate, SimUpdate


class CRUDSim(CRUDBase[Sim, SimCreate, SimUpdate]):
    pass


sim = CRUDSim(model=Sim)
