import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s-%(name)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("Core")
logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    logger.debug("This is a Debug message")
    logger.info("This is a Information message")
    logger.warning("This is a Warning message")
    logger.error("This is a Error message")
    logger.critical("This is a Critical message")
