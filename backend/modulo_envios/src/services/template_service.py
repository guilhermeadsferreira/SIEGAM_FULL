from typing import Dict, List, Any
from .templates.email_template_service import EmailTemplateService
from .templates.whatsapp_template_service import WhatsAppTemplateService


class TemplateService:
    """
    Facade que escolhe qual serviço de template usar com base no canal.
    """

    def __init__(self):
        self.services = {
            "email": EmailTemplateService(),
            "whatsapp": WhatsAppTemplateService(),
        }
    
    def generate_template(self, canal: str, cidades_alertas):
        canal = canal["nomeCanal"].lower()

        if canal not in self.services:
            raise ValueError(f"Canal '{canal}' não suportado.")

        return self.services[canal].generate(cidades_alertas)