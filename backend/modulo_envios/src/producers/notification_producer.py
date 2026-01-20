import json
from ..utils.redis_client import redis_client


class NotificationProducer:
    def __init__(self):
        self.queue_name = "notification_queue"

    def send_to_queue(self, data: dict):
        """
        Envia o payload completo de notificação para a fila de envios.
        """
        print("[NotificationProducer] Enfileirando notificação...")
        redis_client.rpush(self.queue_name, json.dumps(data))
        print(f"[NotificationProducer] Notificação enfileirada para {data.get('canal')} ({len(data.get('usuarios', []))} usuários).")
