import asyncio
from src.redis.listener import listener
from src.lib.logger import logger

async def main():
    logger.info("Starting Redis status listener worker...")
    await listener.start_listening()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
