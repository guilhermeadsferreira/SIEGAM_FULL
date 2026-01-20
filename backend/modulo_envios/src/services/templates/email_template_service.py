from datetime import datetime
from typing import List, Dict, Any
import math
import html
import os


class EmailTemplateService:
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
        city_blocks = ""
        for item in cidades_alertas:
            city_blocks += self.render_city_block(
                cidade=item["cidade"],
                uf=item["uf"],
                alertas=item["alertas"]
            )

        return f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resumo de Avisos Meteorol&oacute;gicos - CEMPA</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            
            {self.header()}

            <div style="padding: 20px;">
                {city_blocks}
            </div>

            {self.footer()}

        </body>
        </html>
        """

    def header(self) -> str:
        return """
        <div style="background-color: #e74c3c; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0;">
            <h2>Resumo de Avisos Meteorológicos</h2>
        </div>
        """

    def footer(self) -> str:
        # Construir URL a partir da variável de ambiente FRONTEND_URL
        frontend = os.getenv("FRONTEND_URL", "").rstrip('/')
        if frontend:
            manage_url = f"{frontend}/manage-profile"
        else:
            # Fallback para rota relativa caso variável não esteja definida
            manage_url = "/manage-profile"

        manage_url_safe = html.escape(manage_url)

        return f"""
        <hr style="border: 0; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="color: #777; font-size: 12px;">Este é um e-mail automático do CEMPA.</p>
        <p style="color: #777; font-size: 12px;">Por favor, não responda a este e-mail.</p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="{manage_url_safe}" 
               style="background-color: #dc3545; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
               Descadastrar ou atualizar preferências
            </a>
        </div>
        """

    def render_city_block(self, cidade: str, uf: str, alertas: List[Dict[str, Any]]) -> str:
        alert_html = ""
        for alerta in alertas:
            alert_html += self.render_alert_block(alerta)

        cidade_safe = html.escape(cidade)
        uf_safe = html.escape(uf)

        return f"""
        <div style="margin-bottom: 30px; padding: 15px; border: 1px solid #eee; border-radius: 5px;">
            <h3 style="margin-bottom: 10px;">Município: {cidade_safe}/{uf_safe}</h3>
            {alert_html}
        </div>
        """

    def render_alert_block(self, alerta: Dict[str, Any]) -> str:
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
        cor = "#e74c3c"
        temp = math.floor(alerta["valor"])
        unidade_safe = html.escape(str(alerta['unidadeMedida']))
        data_safe = html.escape(self._format_data_pt_br(alerta['dataReferencia']))
        periodo_safe = html.escape(str(alerta['periodo']))

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
                <strong>Aviso - Previsão de temperatura mínima baixa</strong>
            </div>

            <div style="padding: 10px;">
                <p><strong>Data:</strong> {data_safe}</p>
                <p>Temperatura mínima prevista é de <strong>{temp} {unidade_safe}</strong>
                no período entre <strong>{periodo_safe}</strong>.</p>
            </div>

            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
        </div>
        """


    def _render_temperatura_alta(self, alerta):
        cor = "#e74c3c"
        temp = math.ceil(alerta["valor"])
        unidade_safe = html.escape(str(alerta['unidadeMedida']))
        data_safe = html.escape(self._format_data_pt_br(alerta['dataReferencia']))
        periodo_safe = html.escape(str(alerta['periodo']))

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
                <strong>Aviso - Previsão de temperatura máxima elevada</strong>
            </div>

            <div style="padding: 10px;">
                <p><strong>Data:</strong> {data_safe}</p>
                <p>Temperatura máxima prevista é de <strong>{temp} {unidade_safe}</strong>
                no período entre <strong>{periodo_safe}</strong>.</p>
            </div>

            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
        </div>
        """


    def _render_umidade_baixa(self, alerta):
        cor = "#f39c12"
        valor = math.floor(alerta["valor"])

        if 30 <= valor <= 60:
            nivel_msg = "Crítico para a saúde humana (30% a 60%)."
        elif 21 <= valor < 30:
            nivel_msg = "Estado de Atenção (21% a 30%)."
            cor = "#e74c3c"
        elif 12 <= valor < 21:
            nivel_msg = "Estado de Alerta (12% a 20%)."
            cor = "#e74c3c"
        elif valor < 12:
            nivel_msg = "Estado de Emergência (abaixo de 12%)."
            cor = "#e74c3c"
        else:
            nivel_msg = "Umidade dentro da normalidade."

        unidade_safe = html.escape(str(alerta['unidadeMedida']))
        data_safe = html.escape(self._format_data_pt_br(alerta['dataReferencia']))
        periodo_safe = html.escape(str(alerta['periodo']))

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
                <strong>Aviso - Previsão de registros de baixa umidade relativa do ar em superfície</strong>
            </div>

            <div style="padding: 10px;">
                <p><strong>Data:</strong> {data_safe}</p>
                <p>Umidade relativa prevista é de <strong>{valor} {unidade_safe}</strong>
                no período entre <strong>{periodo_safe}</strong>.</p>
                <p style="margin-top: 10px;"><em>{nivel_msg}</em></p>
            </div>

            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
        </div>
        """


    def _render_vento(self, alerta):
        cor = "#f39c12"
        valor = math.ceil(alerta["valor"])

        if 12 <= valor < 20:
            nivel_msg = "Brisa fraca (12 km/h – 20 km/h)."
        elif 20 <= valor < 30:
            nivel_msg = "Brisa moderada (20 km/h – 30 km/h)."
        elif 30 <= valor < 40:
            nivel_msg = "Ventania (30 km/h – 40 km/h)."
            cor = "#e74c3c"
        elif 40 <= valor <= 50:
            nivel_msg = "Forte ventania (40 km/h – 50 km/h)."
            cor = "#e74c3c"
        elif valor > 50:
            nivel_msg = "Vento forte (acima de 50 km/h)."
            cor = "#e74c3c"
        else:
            nivel_msg = "Vento dentro da normalidade."

        if valor < 30:
            titulo = "Aviso - Previsão de brisa fraca"
        else:
            titulo = "Aviso - Previsão de ventania ou vento forte"

        unidade_safe = html.escape(str(alerta['unidadeMedida']))
        data_safe = html.escape(self._format_data_pt_br(alerta['dataReferencia']))
        periodo_safe = html.escape(str(alerta['periodo']))

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
                <strong>{titulo}</strong>
            </div>

            <div style="padding: 10px;">
                <p><strong>Data:</strong> {data_safe}</p>
                <p>Velocidade do vento prevista é de <strong>{valor} {unidade_safe}</strong>
                no período entre <strong>{periodo_safe}</strong>.</p>
                <p style="margin-top: 10px;"><em>{nivel_msg}</em></p>
            </div>

            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
        </div>
        """


    def _render_chuva(self, alerta):
        cor = "#f39c12"
        valor = math.ceil(alerta["valor"])

        if 15 <= valor <= 25:
            nivel_msg = "Chuva de intensidade moderada (15 mm/h – 25 mm/h)."
        elif valor > 25:
            nivel_msg = "Chuva de intensidade forte (acima de 25 mm/h)."
            cor = "#e74c3c"
        else:
            nivel_msg = "Chuva fraca ou dentro da normalidade."

        unidade_safe = html.escape(str(alerta['unidadeMedida']))
        data_safe = html.escape(self._format_data_pt_br(alerta['dataReferencia']))
        periodo_safe = html.escape(str(alerta['periodo']))

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
                <strong>Aviso - Previsão de ocorrência de chuva intensa</strong>
            </div>

            <div style="padding: 10px;">
                <p><strong>Data:</strong> {data_safe}</p>
                <p>Precipitação estimada de <strong>{valor} {unidade_safe}</strong>
                no período entre <strong>{periodo_safe}</strong>.</p>
                <p style="margin-top: 10px;"><em>{nivel_msg}</em></p>
            </div>

            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
        </div>
        """


    def _render_generico(self, alerta):
        cor = "#7f8c8d"
        tipo_safe = html.escape(alerta['tipo'].replace('_',' ').capitalize())
        valor_safe = html.escape(str(alerta['valor']))
        unidade_safe = html.escape(str(alerta['unidadeMedida']))
        data_safe = html.escape(self._format_data_pt_br(alerta['dataReferencia']))

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="background-color: {cor}; color: white; padding: 8px; border-radius: 4px;">
                <strong>Aviso - {tipo_safe}</strong>
            </div>
            <div style="padding: 10px;">
                <p><strong>Valor:</strong> {valor_safe}{unidade_safe}</p>
                <p><strong>Data:</strong> {data_safe}</p>
            </div>
            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 15px;">
        </div>
        """
