
import redis.asyncio as redis
import json
import logging
from config import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def test_redis_connection():
    try:
        await redis_client.ping()
        logger.info(f"✅ Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis at {REDIS_HOST}:{REDIS_PORT}: {e}")

async def get_cache(key: str, raw: bool = False):
    try:
        data = await redis_client.get(key)
        if data:
            logger.info(f"Cache HIT for key: {key}")
            return data if raw else json.loads(data)
        logger.info(f"Cache MISS for key: {key}")
    except Exception as e:
        logger.error(f"Redis get_cache error: {e}")
    return None

async def set_cache(key: str, value: any, expire: int = 300): # 5 minutes default
    try:
        await redis_client.set(key, json.dumps(value), ex=expire)
        logger.info(f"Cache SET for key: {key}")
    except Exception as e:
        logger.error(f"Redis set_cache error: {e}")

async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
        logger.info(f"Cache DELETE for key: {key}")
    except Exception as e:
        logger.error(f"Redis delete_cache error: {e}")

async def invalidate_leaderboard():
    await delete_cache("leaderboard_data")
