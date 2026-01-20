import asyncio
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any

from ..services.external_integration_service import ExternalIntegrationService
from ..services.alert_service import AlertService
from ..services.templates.email_template_service import EmailTemplateService
from ..services.templates.whatsapp_template_service import WhatsAppTemplateService
from ..producers.notification_producer import NotificationProducer

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/start")
async def start_alert_processing():
    print("[alerts_routes] Iniciando processamento de alertas...")
    try:
        integrador_service = ExternalIntegrationService()
        alert_service = AlertService()

        alerts = await integrador_service.get_alerts_for_today()

        print("Alertas recebidos:", len(alerts))

        if not alerts:
            return {
                "status": "ok",
                "message": "Nenhum alerta encontrado para hoje."
            }

        # Dispara o processamento em background - CORREÇÃO: o método se chama process_all_alerts

        print("[alerts_routes] Adicionando tarefa de processamento em segundo plano...")
        await alert_service.process_all_alerts(alerts)

        return {
            "status": "ok",
            "count": len(alerts),
            "message": "Processamento iniciado em segundo plano."
        }

    except Exception as e:
        print(f"[alerts_routes] Erro ao iniciar processamento de alertas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email-template", response_class=HTMLResponse)
async def test_email_template(payload: Dict[str, List[Dict[str, Any]]] = Body(...)):
    try:
        cidades_alertas = payload.get("cidades_alertas", [])
        if not cidades_alertas:
            raise HTTPException(status_code=400, detail="Payload inválido. 'cidades_alertas' não encontrado.")

        template_service = EmailTemplateService()
        html_content = template_service.generate(cidades_alertas)
        
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-whatsapp-template", response_class=HTMLResponse)
async def test_whatsapp_template(payload: Dict[str, List[Dict[str, Any]]] = Body(...)):
    try:
        cidades_alertas = payload.get("cidades_alertas", [])
        if not cidades_alertas:
            raise HTTPException(status_code=400, detail="Payload inválido. 'cidades_alertas' não encontrado.")

        template_service = WhatsAppTemplateService()
        html_content = template_service.generate(cidades_alertas)
        
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/test-notification")
async def test_notification(payload: Dict[str, Any] = Body(...)):
    try:
        producer = NotificationProducer()

        producer.send_to_queue(payload)

        return {
            "status": "ok",
            "message": "Notificação enviada para a fila.",
            "payload_enviado": payload
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))