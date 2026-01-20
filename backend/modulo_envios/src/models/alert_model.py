from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Literal, Optional

class Alert(BaseModel):
    cidade: str = Field(..., example="São Paulo")
    uf: str = Field(..., example="SP")
    tipo_alerta: Literal["chuva intensa", "vento", "humidade", "temperatura máxima", "temperatura mínima"]
    unidade_medida: str = Field(..., example="mm", description="Unidade de medida do valor")
    valor: float
    valor_maximo: Optional[float] = None
    diferenca: Optional[float] = None
    segundos: Optional[int] = None
    data: date
    horario: time
    data_geracao: datetime
