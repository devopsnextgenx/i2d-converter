import logging
from fileHelper import createOutputFolder

def getLogger(name, filename = "logs/i2c.log", level = logging.DEBUG):
    createOutputFolder('logs')
    logging.basicConfig(level="WARNING",
        format="%(asctime)s.%(msecs)03d - [%(levelname)8s:%(name)10s] - %(message)s ",
        datefmt='%Y%m%d %H:%M:%S',
        force=True,
        handlers=[
            logging.FileHandler(filename),
            logging.StreamHandler()
        ])
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

def main():
    logger = getLogger('main')
    # Test messages
    logger.debug("debug Message")
    logger.info("info Message")
    logger.warning("warning Message")
    logger.error("error Message")
    logger.critical("critical Message")

if __name__ == "__main__":
    main()