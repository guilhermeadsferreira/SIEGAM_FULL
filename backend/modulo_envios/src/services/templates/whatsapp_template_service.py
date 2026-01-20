from datetime import datetime
from typing import List, Dict, Any
import math
import os

class WhatsAppTemplateService:

    @staticmethod
    def _format_data_pt_br(data_str: str) -> str:
        """
        Converte data no formato YYYY-MM-DD para DD/MM/YYYY (pt-BR)
        Exemplo: '2025-12-05' -> '05/12/2025'
        """
        try:
            if not data_str:
                return "N/A"
            # Suporta formato YYYY-MM-DD
            if isinstance(data_str, str) and len(data_str) == 10:
                data_obj = datetime.strptime(data_str, "%Y-%m-%d")
                return data_obj.strftime("%d/%m/%Y")
            return str(data_str)
        except (ValueError, AttributeError):
            return str(data_str)
        
    def generate(self, cidades_alertas):
        message = self.header()

        for item in cidades_alertas:
            cidade = item["cidade"]
            uf = item["uf"]
            alertas = item["alertas"]

            message += self.render_city_block(cidade, uf, alertas)

        message += self.footer()

        return message

    def header(self) -> str:
        return (
            "🌦️ *Resumo de Avisos Meteorológicos*\n"
            "_Centro de Excelência em Estudos, Monitoramento e Previsões Ambientais do Cerrado (CEMPA-Cerrado)_\n\n"
        )

    def footer(self) -> str:
        # Construir URL de gerenciamento a partir da variável de ambiente FRONTEND_URL
        frontend = os.getenv("FRONTEND_URL", "").rstrip('/')
        if frontend:
            manage_url = f"{frontend}/manage-profile"
        else:
            manage_url = "/manage-profile"

        return (
            "\n🤖 _Mensagem automática do CEMPA._\n"
            f"_Para gerenciar notificações, acesse: {manage_url}_"
        )

    def render_city_block(self, cidade: str, uf: str, alertas: List[Dict[str, Any]]) -> str:
        text = f"📍 *{cidade}/{uf}*\n"
        if not alertas:
            return text + "Nenhum alerta registrado.\n\n"

        for alerta in alertas:
            text += self.render_alert(alerta)

        text += "\n"
        return text

    def render_alert(self, alerta: Dict[str, Any]) -> str:
        tipo = alerta["eventoNome"].lower()

        if tipo == "temperatura baixa":
            return self._render_temperatura_baixa(alerta)
        if tipo == "temperatura alta":
            return self._render_temperatura_alta(alerta)
        if tipo == "umidade baixa":
            return self._render_umidade_baixa(alerta)
        if tipo == "vento":
            return self._render_vento(alerta)
        if tipo == "chuva":
            return self._render_chuva(alerta)

        return self._render_generico(alerta)

    def _render_temperatura_baixa(self, alerta):
        temp = math.floor(alerta["valor"])

        return (
            "❄️ *Aviso - Previsão de temperatura mínima baixa*\n"
            f"• *Data:* {self._format_data_pt_br(alerta['dataReferencia'])}\n"
            f"• Temperatura mínima prevista: *{temp} {alerta['unidadeMedida']}*\n"
            f"• Período: {alerta['periodo']}\n"
            "----------------------\n"
        )

    def _render_temperatura_alta(self, alerta):
        temp = math.ceil(alerta["valor"])

        return (
            "🔥 *Aviso - Previsão de temperatura máxima elevada*\n"
            f"• *Data:* {self._format_data_pt_br(alerta['dataReferencia'])}\n"
            f"• Temperatura máxima prevista: *{temp} {alerta['unidadeMedida']}*\n"
            f"• Período: {alerta['periodo']}\n"
            "----------------------\n"
        )

    def _render_umidade_baixa(self, alerta):
        valor = math.floor(alerta["valor"])

        if 30 <= valor <= 60:
            nivel_msg = "Crítico para a saúde humana (30% a 60%)."
        elif 21 <= valor < 30:
            nivel_msg = "Estado de Atenção (21% a 30%)."
        elif 12 <= valor < 21:
            nivel_msg = "Estado de Alerta (12% a 20%)."
        elif valor < 12:
            nivel_msg = "Estado de Emergência (abaixo de 12%)."
        else:
            nivel_msg = "Umidade dentro da normalidade."

        return (
            "💧 *Aviso - Baixa Umidade Relativa do Ar*\n"
            f"• *Data:* {self._format_data_pt_br(alerta['dataReferencia'])}\n"
            f"• Umidade prevista: *{valor} {alerta['unidadeMedida']}*\n"
            f"• *Nível:* _{nivel_msg}_\n"
            f"• Período: {alerta['periodo']}\n"
            "----------------------\n"
        )

    def _render_vento(self, alerta):
        valor = math.ceil(alerta["valor"])

        if 12 <= valor < 20:
            nivel_msg = "Brisa fraca (12–20 km/h)."
        elif 20 <= valor < 30:
            nivel_msg = "Brisa moderada (20–30 km/h)."
        elif 30 <= valor < 40:
            nivel_msg = "Ventania (30–40 km/h)."
        elif 40 <= valor <= 50:
            nivel_msg = "Forte ventania (40–50 km/h)."
        elif valor > 50:
            nivel_msg = "Vento forte (acima de 50 km/h)."
        else:
            nivel_msg = "Vento dentro da normalidade."

        return (
            "💨 *Aviso - Ventania / Vento Forte*\n"
            f"• *Data:* {self._format_data_pt_br(alerta['dataReferencia'])}\n"
            f"• Velocidade prevista: *{valor} {alerta['unidadeMedida']}*\n"
            f"• *Nível:* _{nivel_msg}_\n"
            f"• Período: {alerta['periodo']}\n"
            "----------------------\n"
        )

    def _render_chuva(self, alerta):
        valor = math.ceil(alerta["valor"])

        if 15 <= valor <= 25:
            nivel_msg = "Chuva moderada (15–25 mm/h)."
        elif valor > 25:
            nivel_msg = "Chuva forte (acima de 25 mm/h)."
        else:
            nivel_msg = "Precipitação fraca ou normal."

        return (
            "🌧️ *Aviso - Previsão de ocorrência de chuva intensa*\n"
            f"• *Data:* {self._format_data_pt_br(alerta['dataReferencia'])}\n"
            f"• Precipitação estimada: *{valor} {alerta['unidadeMedida']}*\n"
            f"• *Nível:* _{nivel_msg}_\n"
            f"• Período: {alerta['periodo']}\n"
            "----------------------\n"
        )

    def _render_generico(self, alerta):
        return (
            f"⚠️ *Aviso - {alerta['tipo'].capitalize()}*\n"
            f"• Valor: {alerta['valor']}{alerta['unidadeMedida']}\n"
            f"• Data: {self._format_data_pt_br(alerta['dataReferencia'])}\n"
            "----------------------\n"
        )

