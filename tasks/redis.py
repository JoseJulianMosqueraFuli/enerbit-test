import redis
from config import Config

redis_host = Config.REDIS_HOST
redis_port = Config.REDIS_PORT
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
