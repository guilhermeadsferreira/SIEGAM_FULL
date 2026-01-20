import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Configurações Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Nomes das filas
ALERT_QUEUE = os.getenv("ALERT_QUEUE", "alert-processing-queue")
NOTIFICATION_QUEUE = os.getenv("NOTIFICATION_QUEUE", "notification-send-queue")
