from datetime import date
from pydantic import BaseModel
from typing import List

class DailyAnalytics(BaseModel):
    date: date
    customers: int
    devices: int
    payments: float
    vendors: int

class AnalyticsResponse(BaseModel):
    total_customers: int
    total_devices: int
    total_payments: float
    total_vendors: int
    daily_data: List[DailyAnalytics]
