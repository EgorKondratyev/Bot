from loguru import logger


# logger.add("DEBUG.log", format="{time} - {level} {message}", level="DEBUG")
logger.add("INFO.log", format="{time} - {level} Message: {message}", level="INFO")
logger.add("WARNING.log", format="{time} - {level} Message: {message}", level="WARNING")
