"""Resolve destinatários por cidade/evento via query batch no banco."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from domain.entities import AlertPayload, UserWithPreference
from infra.database.usuario_repository import get_users_with_preferences_batch
from infra.logger import JsonLogger


class ResolverService:
    """Resolve usuários inscritos para cada alerta (cidade + evento) em batch."""

    def __init__(self, logger: JsonLogger):
        self._logger = logger

    def resolve(self, alerts: list[AlertPayload]) -> dict[str, dict[str, Any]]:
        """
        Agrupa alertas por (id_cidade, id_evento), busca usuários em batch,
        retorna dict[user_id, {usuario: UserWithPreference, alertas: list[AlertPayload]}].
        """
        if not alerts:
            return {}

        pairs = list(set((a.id_evento, a.id_cidade) for a in alerts))
        users_by_pair = get_users_with_preferences_batch(pairs)

        users_alerts: dict[str, dict[str, Any]] = {}

        for alert in alerts:
            key = (alert.id_evento, alert.id_cidade)
            users = users_by_pair.get(key, [])
            for user_data in users:
                uid = user_data["id"]
                if uid not in users_alerts:
                    users_alerts[uid] = {
                        "usuario": UserWithPreference(
                            id=user_data["id"],
                            nome=user_data["nome"],
                            email=user_data.get("email"),
                            whatsapp=user_data.get("whatsapp"),
                            personalizavel=user_data.get("personalizavel", False),
                            valor=user_data.get("valor"),
                            canais_preferidos=user_data.get("canais_preferidos", []),
                        ),
                        "alertas": [],
                    }
                users_alerts[uid]["alertas"].append(alert)

        self._logger.info(
            "Destinatários resolvidos",
            total_alertas=len(alerts),
            pares_unicos=len(pairs),
            usuarios_unicos=len(users_alerts),
        )
        return users_alerts
