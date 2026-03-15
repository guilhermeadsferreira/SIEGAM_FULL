"""Constantes de domínio para o módulo de notificações."""

REDIS_NOTIFICATIONS_QUEUE = "etl:notifications:ready"
REDIS_DEAD_LETTER_QUEUE = "etl:notifications:dead-letter"

STATUS_SUCESSO = "Sucesso"
STATUS_FALHA = "Falha"

CANAL_EMAIL = "email"
CANAL_WHATSAPP = "whatsapp"
