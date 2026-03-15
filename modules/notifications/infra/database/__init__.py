"""Database infrastructure."""

from infra.database.catalogo_repository import get_canais, get_status_by_canal
from infra.database.envio_repository import envio_exists, insert_envio
from infra.database.postgres import get_connection
from infra.database.usuario_repository import get_users_with_preferences_batch

__all__ = [
    "get_connection",
    "get_canais",
    "get_status_by_canal",
    "envio_exists",
    "insert_envio",
    "get_users_with_preferences_batch",
]
