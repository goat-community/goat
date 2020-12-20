#Code based on https://github.com/hackersandslackers/psycopg2-tutorial/blob/master/psycopg2_tutorial/db.py

"""Custom logger."""
from sys import stdout
from loguru import logger


def create_logger():
    """Create custom logger."""
    logger.remove()
    logger.add(
        stdout,
        colorize=True,
        level="INFO",
        catch=True,
        format="<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | "
        + "<light-green>{level}</light-green>: "
        + "<light-white>{message}</light-white>"
    )
    return logger


LOGGER = create_logger()