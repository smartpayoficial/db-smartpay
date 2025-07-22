from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    customers: int
    devices: int
    payments: float
    vendors: int
