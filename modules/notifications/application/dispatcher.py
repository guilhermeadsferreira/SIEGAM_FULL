"""Orquestra renderização, envio e registro de notificações."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Protocol

from domain.entities import AlertPayload, UserWithPreference
from domain.value_objects import Channel
from infra.logger import JsonLogger


class TemplateRenderer(Protocol):
    def render(self, cidades_alertas: list[dict]) -> str: ...


class Sender(Protocol):
    def send(self, destinatarios: list[dict], conteudo: str) -> bool: ...


class DispatcherService:
    """Formata alertas por cidade, renderiza template por canal, despacha e registra."""

    def __init__(
        self,
        logger: JsonLogger,
        email_renderer: TemplateRenderer,
        whatsapp_renderer: TemplateRenderer,
        email_sender: Sender,
        whatsapp_sender: Sender,
        insert_envio_fn: callable,
        envio_exists_fn: callable,
        get_canal_id_fn: callable,
        get_status_id_fn: callable,
    ):
        self._logger = logger
        self._renderers = {
            Channel.EMAIL: email_renderer,
            Channel.WHATSAPP: whatsapp_renderer,
        }
        self._senders = {
            Channel.EMAIL: email_sender,
            Channel.WHATSAPP: whatsapp_sender,
        }
        self._insert_envio = insert_envio_fn
        self._envio_exists = envio_exists_fn
        self._get_canal_id = get_canal_id_fn
        self._get_status_id = get_status_id_fn

    def dispatch(
        self,
        usuario: UserWithPreference,
        alertas: list[AlertPayload],
    ) -> None:
        """Para cada canal preferido do usuário: renderiza, envia e registra."""
        if not alertas:
            return

        cidades_alertas = self._formatar_alertas_por_cidade(alertas)
        canais = self._get_canais_from_usuario(usuario)

        for canal_info in canais:
            canal_nome = (canal_info.get("nomeCanal") or canal_info.get("nome_canal") or "").lower()
            canal_id = canal_info.get("id") or self._get_canal_id(canal_nome)

            if canal_nome not in ("email", "whatsapp"):
                self._logger.warning("Canal não suportado", canal=canal_nome)
                continue

            channel = Channel.EMAIL if canal_nome == "email" else Channel.WHATSAPP
            renderer = self._renderers.get(channel)
            sender = self._senders.get(channel)

            if not renderer or not sender:
                continue

            try:
                conteudo = renderer.render(cidades_alertas)
                destinatarios = [{
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "whatsapp": usuario.whatsapp,
                }]
                success = sender.send(destinatarios, conteudo)
                status_name = "Sucesso" if success else "Falha"
            except Exception as e:
                self._logger.exception("Erro ao enviar notificação", canal=canal_nome, error=str(e))
                status_name = "Falha"

            self._register_envios(usuario.id, canal_id, alertas, status_name)

    def _formatar_alertas_por_cidade(self, alertas: list[AlertPayload]) -> list[dict]:
        """Agrupa alertas por cidade."""
        by_city: dict[str, list[dict]] = defaultdict(list)
        city_names: dict[str, str] = {}
        for a in alertas:
            key = a.id_cidade
            city_names[key] = a.nome_cidade
            by_city[key].append({
                "id": a.aviso_id,
                "id_cidade": a.id_cidade,
                "id_evento": a.id_evento,
                "nome_cidade": a.nome_cidade,
                "nome_evento": a.nome_evento,
                "valor": a.valor,
                "unidade_medida": a.unidade_medida,
                "horario": a.horario,
                "data_referencia": a.data_referencia,
            })

        return [
            {"cidade": city_names.get(k, ""), "uf": "GO", "alertas": alist}
            for k, alist in by_city.items()
        ]

    def _get_canais_from_usuario(self, usuario: UserWithPreference) -> list[dict]:
        canais = usuario.canais_preferidos or []
        if not canais:
            return []
        return canais if isinstance(canais[0], dict) else []

    def _register_envios(
        self,
        id_usuario: str,
        id_canal: str,
        alertas: list[AlertPayload],
        status_name: str,
    ) -> None:
        """Registra cada envio (aviso × usuário) na tabela envios, com idempotency check."""
        id_status = self._get_status_id(id_canal, status_name)
        if not id_status:
            self._logger.warning("Status não encontrado", status=status_name, canal=id_canal)
            return

        for alerta in alertas:
            if self._envio_exists(id_canal, alerta.aviso_id, id_usuario):
                self._logger.debug("Envio já registrado, ignorando", aviso_id=alerta.aviso_id)
                continue
            try:
                self._insert_envio(id_canal, alerta.aviso_id, id_usuario, id_status)
            except Exception as e:
                self._logger.exception(
                    "Erro ao registrar envio",
                    aviso_id=alerta.aviso_id,
                    error=str(e),
                )
