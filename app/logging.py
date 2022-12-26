from loguru import logger

logger.add("logs/logs.json", format="{time} {level} {message}", level="INFO", 
    rotation="1 week", compression="zip", serialize=True)