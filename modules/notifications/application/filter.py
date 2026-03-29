"""Filtra alertas por preferência do usuário."""

from __future__ import annotations

from domain.entities import AlertPayload, UserWithPreference
from domain.value_objects import is_alert_critical
from infra.logger import JsonLogger


class FilterService:
    """
    Aplica filtragem por preferência do usuário.
    Threshold de temperatura está no ETL, então aqui só: crítico, personalizável, valor.
    """

    def __init__(self, logger: JsonLogger):
        self._logger = logger

    def apply(
        self, alertas: list[AlertPayload], usuario: UserWithPreference
    ) -> list[AlertPayload]:
        """Retorna apenas alertas que passaram no filtro para o usuário."""
        filtered = []
        for alerta in alertas:
            if self._should_send(alerta, usuario):
                filtered.append(alerta)
        return filtered

    def _should_send(self, alerta: AlertPayload, usuario: UserWithPreference) -> bool:
        tipo = alerta.nome_evento.lower()
        valor = alerta.valor
        personalizavel = usuario.personalizavel
        valor_preferencia = usuario.valor
        self._logger.info(
            "[DEBUG FILTER]",
            tipo=tipo,
            valor=valor,
            personalizavel=personalizavel,
            valor_preferencia=valor_preferencia,
            user_id=usuario.id,
        )

        # Eventos sem nível (chuva, temp alta, temp baixa): sempre envia (ETL já filtrou temp)
        if tipo in ("chuva", "temperatura alta", "temperatura baixa"):
            if not personalizavel:
                return True
            if valor_preferencia is None:
                return True
            if tipo == "temperatura baixa":
                return valor < valor_preferencia
            return valor > valor_preferencia

        # Vento e umidade
        if valor_preferencia is None:
            return is_alert_critical(tipo, valor)

        if not personalizavel:
            return is_alert_critical(tipo, valor)

        if tipo == "umidade baixa":
            return valor < valor_preferencia
        return valor > valor_preferencia
