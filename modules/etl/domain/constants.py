"""Constantes de domínio para application logs."""

# Tarefas do pipeline
TASK_NAME_ETL = "etl"
TASK_NAME_LOAD = "load"
TASK_NAME_DISPATCH = "dispatch"

# Status de execução
STATUS_STARTED = "STARTED"
STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_SUCCESS = "SUCCESS"
STATUS_ERROR = "ERROR"

# Infraestrutura
REDIS_NOTIFICATIONS_QUEUE = "etl:notifications:ready"
