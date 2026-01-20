from pydantic import BaseModel, Field
from typing import List
from datetime import date, time, datetime
from src.models.alert_model import Alert

class CityAlerts(BaseModel):
    cidade: str = Field(..., example="São Paulo")
    uf: str = Field(..., example="SP")
    alertas: List[Alert]
