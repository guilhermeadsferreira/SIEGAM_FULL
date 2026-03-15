"""Protocols para injeção de dependências."""

from __future__ import annotations

from typing import Any, Protocol


class Sender(Protocol):
    """Protocol para envio de notificações (e-mail, WhatsApp)."""

    def send(self, destinatarios: list[dict[str, Any]], conteudo: str) -> bool:
        """Envia conteúdo para a lista de destinatários. Retorna True se sucesso."""
        ...


class TemplateRenderer(Protocol):
    """Protocol para renderização de templates por canal."""

    def render(self, cidades_alertas: list[dict[str, Any]]) -> str:
        """Renderiza o conteúdo formatado (HTML ou texto) para o canal."""
        ...
