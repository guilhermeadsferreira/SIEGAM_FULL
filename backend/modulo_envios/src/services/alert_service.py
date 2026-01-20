import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import traceback
from typing import Any, Dict, List

from .external_integration_service import ExternalIntegrationService
from .template_service import TemplateService
from ..producers.notification_producer import NotificationProducer
from ..utils.config_parser import ConfigParser


class AlertService:
    def __init__(self):
        self.integration_service = ExternalIntegrationService()
        self.template_service = TemplateService()
        self.notification_producer = NotificationProducer()
        self.config = ConfigParser()
        # Constante para diferença mínima de temperatura
        self.minimum_diff_temperature = 5

    @staticmethod
    def _get_user_static_data(user: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": user["id"],
            "nome": user["nome"],
            "email": user.get("email"),
            "whatsapp": user.get("whatsapp"),
            "dataCriacao": user.get("dataCriacao"),
            "dataUltimaEdicao": user.get("dataUltimaEdicao"),
            "nivelAcesso": user.get("nivelAcesso"),
            "canaisPreferidos": user.get("canaisPreferidos", []),
        }

    @staticmethod
    def _calcular_periodo(horario_str: str) -> str:
        try:
            hora = datetime.strptime(horario_str, "%H:%M:%S")
        except Exception:
            hora = datetime.strptime(horario_str, "%H:%M")

        inicio = (hora - timedelta(hours=1)).strftime("%H:%M")
        fim = (hora + timedelta(hours=1)).strftime("%H:%M")
        return f"{inicio} às {fim}"

    @staticmethod
    def _is_alert_critical(evento_nome: str, valor: float) -> bool:
        """
        Determina se um alerta é crítico baseado no tipo de evento e valor.
        Sem níveis (sempre crítico): Chuva, Temperatura Alta, Temperatura Baixa
        Com níveis:
        - Vento: crítico se valor >= 30
        - Umidade Baixa: crítico se valor <= 30
        """
        evento_lower = evento_nome.lower() if evento_nome else ""

        # Eventos sem nível (sempre críticos)
        if evento_lower in ["chuva", "temperatura alta", "temperatura baixa"]:
            return True

        # Vento: crítico acima de 30
        if evento_lower == "vento":
            return valor >= 30

        # Umidade Baixa: crítico abaixo de 30
        if evento_lower == "umidade baixa":
            return valor <= 30

        # Padrão: considerar como crítico
        return True

    def _is_temperature_critical(
        self, evento_nome: str, valor: float, polygon_name: str
    ) -> tuple:
        """
        Verifica se temperatura é crítica comparando com limiares configurados.
        Retorna (is_critical, threshold, difference) onde:
        - is_critical: bool indicando se deve enviar notificação
        - threshold: valor do limiar usado
        - difference: diferença entre valor e limiar
        
        Para temperatura máxima: crítica se valor > threshold e diferença >= minimum_diff_temperature
        Para temperatura mínima: crítica se valor < threshold e diferença <= -minimum_diff_temperature
        """
        evento_lower = evento_nome.lower() if evento_nome else ""
        month = datetime.now().month
        if evento_lower == "temperatura alta":
            max_threshold = self.config.get_monthly_temp_threshold(polygon_name, month)
            if max_threshold == 0:
                max_threshold = None
            
            if not max_threshold:
                return (False, None, None)
            
            diff = valor - max_threshold
            is_critical = valor > max_threshold and diff >= self.minimum_diff_temperature
            return (is_critical, max_threshold, diff)
        
        elif evento_lower == "temperatura baixa":
            min_threshold = self.config.get_monthly_temp_min_threshold(polygon_name, month)
            if min_threshold == 0:
                min_threshold = None
            
            if not min_threshold:
                return (False, None, None)
            
            diff = valor - min_threshold
            is_critical = valor < min_threshold and diff <= -self.minimum_diff_temperature
            return (is_critical, min_threshold, diff)
        
        return (False, None, None)

    def _filter_alerts_by_preference(
        self, alertas: List[Dict[str, Any]], user: Dict[str, Any], polygon_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Filtra alertas baseado nas preferências do usuário.
        Para temperatura: verifica limiares configurados
        Se personalizavel=false: alerta deve ser crítico (sem personalização)
        Se personalizavel=true: alerta deve ser maior/menor (conforme evento) que o valor da preferência
        """
        filtered = []
        for item in alertas:
            alerta = item["alerta"]
            evento_nome = item["evento"]["nome"]
            valor_alerta = alerta.get("valor", 0)

            evento_lower = evento_nome.lower() if evento_nome else ""

            personalizavel = user.get("personalizavel", False)
            valor_preferencia = user.get("valor")
            
            # Verificar se é temperatura (necessita limiares configurados)
            if evento_lower in ["temperatura alta", "temperatura baixa"]:
                is_critical, threshold, diff = self._is_temperature_critical(
                    evento_nome, valor_alerta, polygon_name
                )
                
                if is_critical:
                    filtered.append(item)
                    continue
                
                # Se personalizavel=false, ignorar
                if not personalizavel:
                    continue
                
                # Se personalizavel=true, comparar com valor da preferência
                if valor_preferencia is None:
                    continue
                
                # Temperatura máxima: enviar se valor_alerta > valor_preferencia
                if evento_lower == "temperatura alta":
                    if valor_alerta > valor_preferencia:
                        filtered.append(item)
                # Temperatura mínima: enviar se valor_alerta < valor_preferencia
                elif evento_lower == "temperatura baixa":
                    if valor_alerta < valor_preferencia:
                        filtered.append(item)
            else:
                # Para demais eventos (chuva, vento, umidade), usar lógica original
                
                # Se não há preferência configurada, considerar como crítico (enviar)
                if valor_preferencia is None:
                    if self._is_alert_critical(evento_nome, valor_alerta):
                        filtered.append(item)
                    continue

                # Se personalizavel=false, verificar se é crítico
                if not personalizavel:
                    if self._is_alert_critical(evento_nome, valor_alerta):
                        filtered.append(item)
                    continue

                # Se personalizavel=true, comparar com valor da preferência
                # Eventos que devem ser menor: Umidade Baixa
                if evento_lower == "umidade baixa":
                    # Enviar se valor_alerta < valor_preferencia (mais crítico)
                    if valor_alerta < valor_preferencia:
                        filtered.append(item)
                else:
                    # Demais eventos: enviar se valor_alerta > valor_preferencia
                    if valor_alerta > valor_preferencia:
                        filtered.append(item)

        return filtered

    def _formatar_alertas_por_cidade(self, alertas_user: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Recebe os alertas completos (alerta + cidade + evento)
        Agrupa por cidade e formata cada alerta para envio ao template.
        """
        cidades_dict = defaultdict(list)

        for item in alertas_user:
            cidade_id = item["cidade"]["id"]
            cidades_dict[cidade_id].append(item)

        cidades_alertas = []

        for cidade_id, itens in cidades_dict.items():
            cidade_nome = itens[0]["cidade"]["nome"]
            alertas_formatados = []

            for item in itens:
                alerta_original = item["alerta"]
                evento_nome = item["evento"]["nome"]
                periodo = self._calcular_periodo(alerta_original.get("horario"))

                alerta_formatado = {
                    **alerta_original,
                    "eventoNome": evento_nome,
                    "periodo": periodo,
                }
                alertas_formatados.append(alerta_formatado)

            cidades_alertas.append(
                {
                    "cidade": cidade_nome,
                    "uf": "GO",
                    "alertas": alertas_formatados,
                }
            )

        return cidades_alertas

    async def process_all_alerts(self, alerts: List[Dict[str, Any]]):
        try:
            # 1. Agrupar alertas por cidade
            grouped_by_city = defaultdict(list)
            for alert in alerts:
                grouped_by_city[alert["idCidade"]].append(alert)

            print(f"[AlertService] {len(grouped_by_city)} cidades encontradas.")

            users_alerts: Dict[str, Dict[str, Any]] = {}

            # 2. Processar cidade por cidade
            for cidade_id, alertas_da_cidade in grouped_by_city.items():


                # Para cada alerta da cidade, buscar usuários e vincular alerta
                for alert in alertas_da_cidade:
                    id_evento = alert["idEvento"]

                    try:
                        usuarios = await self.integration_service.get_users_by_city_and_alert(
                            cidade_id, id_evento
                        )
                    except Exception as e:
                        print(
                            f"[AlertService] Erro consulta usuários cidade={cidade_id}, evento={id_evento}: {e}"
                        )
                        continue

                    if not usuarios:
                        continue

                    # Associar cada alerta a cada usuário (com filtro de preferências)
                    for user_full in usuarios:
                        uid = user_full["id"]

                        if uid not in users_alerts:
                            users_alerts[uid] = {
                                "usuario": self._get_user_static_data(user_full),
                                "alertas": [],
                            }

                        alerta_item = {
                            "alerta": alert,
                            "cidade": {
                                "id": user_full.get("cidadeId"),
                                "nome": user_full.get("cidadeNome"),
                            },
                            "evento": {
                                "id": user_full.get("eventoId"),
                                "nome": user_full.get("eventoNome"),
                            },
                        }

                        # Filtrar alerta baseado na preferência do usuário (passando polygon_name)
                        # polygon_name é extraído do primeiro alerta com esse id_evento e cidade
                        polygon_name = alert.get("nomeCidade")
                        if self._filter_alerts_by_preference([alerta_item], user_full, polygon_name):
                            users_alerts[uid]["alertas"].append(alerta_item)

                await asyncio.sleep(0)

            print(
                f"[AlertService] Preparando notificações para {len(users_alerts)} usuários."
            )

            # 3. Geração de templates + envio
            for uid, info in users_alerts.items():
                user = info["usuario"]
                alertas_user = info["alertas"]
                
                # Garantir que apenas usuários com alertas não-vazios recebem notificações
                if not alertas_user:
                    print(f"[AlertService] Usuário {uid} não possui alertas após filtro. Pulando...")
                    continue
                
                canais = user.get("canaisPreferidos", [])

                cidades_alertas = self._formatar_alertas_por_cidade(alertas_user)

                for canal in canais:
                    conteudo = self.template_service.generate_template(
                        canal, cidades_alertas
                    )
                    self.notification_producer.send_to_queue(
                        {
                            "canal": canal,
                            "usuarios": [user],
                            "conteudo": conteudo,
                            "alertas": alertas_user,
                        }
                    )

        except Exception as e:
            print(f"[AlertService] ERRO INESPERADO: {e}")
            traceback.print_exc()

        print("[AlertService] Notificações enviadas para fila.")
        return {"status": "ok", "usuarios": len(users_alerts)}
