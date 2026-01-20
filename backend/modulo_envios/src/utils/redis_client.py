import redis
from src.config import REDIS_HOST, REDIS_PORT

# Cria a conexão Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)
