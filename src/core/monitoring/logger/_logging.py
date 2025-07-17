import logging
import logging.config

from settings import settings


class _ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        """Only lets through log messages with log level below ERROR ."""
        return record.levelno < logging.ERROR


ROOT_LEVEL = "INFO" if settings.APP_ENVIRONMENT in [None, "prod"] else "DEBUG"


def get_app_log_configs():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "": {  # root logger
                "level": ROOT_LEVEL,  # "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "DEBUG",
                "handlers": ["default"],
            },
            "uvicorn.access": {
                "level": "DEBUG",
                "handlers": ["default"],
            },
        },
    }


def get_logger(name: str, *, level: int = ROOT_LEVEL):
    logging.config.dictConfig(get_app_log_configs())
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
