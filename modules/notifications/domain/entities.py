"""Entidades de domínio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AlertPayload:
    """Alerta recebido da fila Redis (publicado pelo ETL)."""
    aviso_id: str
    id_cidade: str
    id_evento: str
    nome_cidade: str
    nome_evento: str
    valor: float
    unidade_medida: str
    horario: str | None
    data_referencia: str


@dataclass
class ExecutionPayload:
    """Payload completo da fila etl:notifications:ready."""
    execution_id: str
    date: str
    avisos_count: int
    alerts: list[AlertPayload]


@dataclass
class UserWithPreference:
    """Usuário com dados de preferência para um evento/cidade específico."""
    id: str
    nome: str
    email: str | None
    whatsapp: str | None
    personalizavel: bool
    valor: float | None
    canais_preferidos: list[dict[str, Any]]


@dataclass
class Notification:
    """Registro de envio a persistir na tabela envios."""
    id_canal: str
    id_aviso: str
    id_usuario: str
    id_status: str
