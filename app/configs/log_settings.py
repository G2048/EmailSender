import json
import logging.config
import re

"""
Description: Log settings
Example of usage:

# Add in main.py
>>> from app.configs import (
    get_appsettings,
    get_database_settings,
    get_logger,
)

>>> set_appname(get_appsettings().APP_NAME)
>>> set_appversion(get_appsettings().APP_VERSION)
>>> set_debug_level(get_appsettings().DEBUG)

# In another module:
>>> import logging
>>> logger = logging.getLogger("stdout")
>>> logger.debug("hello world")
>>> logger.info("hello world")
>>> logger.warning("hello world")


# If you are using the uvicorn:
>>> from log_config import LogConfig
...
>>> if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=LogConfig)

"""


DEBUG: bool = False
LOG_LEVEL = "INFO"
SQL_LEVEL = "WARNING"
_appname = "appname"
_version = "1.0.0"


def set_appversion(version: str):
    global _version
    _version = version


class JSONFormatter(logging.Formatter):
    _pattern = re.compile(r"%\((\w+)\)s")
    COUNTER = 0

    def formatMessage(self, record) -> str:
        ready_message: dict = {}
        values = record.__dict__

        self.COUNTER += 1
        logger_name: str = values["name"]
        ready_message["app.name"] = "appname".lower()
        ready_message["app.version"] = "1.0.0"
        ready_message["app.logger"] = logger_name
        ready_message["time"] = self.formatTime(record, self.datefmt)
        ready_message["level"] = values.get("levelname")
        ready_message["log_id"]: int = self.COUNTER

        if record.exc_info:
            ready_message["exc_text"] = self.formatException(record.exc_info)
        if record.stack_info:
            ready_message["stack"] = self.formatStack(record.stack_info)

        for value_name in self._pattern.findall(self._fmt):
            value = values.get(value_name)
            ready_message.update({value_name: value})

        if logger_name.startswith("uvicorn") and len(record.args) == 5:
            ready_message.pop("message", None)
            ready_message["client_addr"] = record.args[0]
            ready_message["method"] = record.args[1]
            ready_message["path"] = record.args[2]
            ready_message["http_version"] = record.args[3]
            ready_message["status"] = record.args[4]

        return json.dumps(ready_message, ensure_ascii=False)


class RouterFilter(logging.Filter):
    endpoints = ("/metrics", "/health")

    def filter(self, record) -> bool:
        assert type(record.args) is tuple
        return not (len(record.args) > 2 and record.args[2] in self.endpoints)


LogConfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "details": {
            "class": "logging.Formatter",
            "format": "%(asctime)s::%(levelname)s::%(filename)s::%(levelno)s::%(lineno)s::%(message)s",
            "incremental": True,
            "encoding": "UTF-8",
        },
        "json": {
            "()": JSONFormatter,
            "format": "%(filename)s::%(lineno)s::%(message)s",
        },
    },
    "filters": {
        "router": {
            "()": RouterFilter,
        },
    },
    "handlers": {
        "rotate": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{_appname}.log",
            "mode": "w",
            "level": LOG_LEVEL,
            "maxBytes": 204800,
            "backupCount": 15,
            "formatter": "details",
            "filters": ["router"],
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "stream": "ext://sys.stderr",
            "formatter": "details",
            "filters": ["router"],
        },
        "json": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "stream": "ext://sys.stderr",
            "formatter": "json",
            "filters": ["router"],
        },
    },
    "loggers": {
        "root": {
            "level": "NOTSET",
        },
        "stdout": {
            "level": LOG_LEVEL,
            "handlers": ["json"],
            "propagate": False,
        },
        "asyncio": {
            "level": LOG_LEVEL,
            "handlers": ["json"],
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": SQL_LEVEL,
            "handlers": ["json"],
            "propagate": False,
        },
        "sqlalchemy.pool": {
            "level": SQL_LEVEL,
            "handlers": ["json"],
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["json"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["json"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["json"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}


def get_logger(name="stdout"):
    logging.config.dictConfig(LogConfig)
    return logging.getLogger(name)


def set_appname(name: str):
    LogConfig["handlers"]["rotate"]["filename"] = f"{name}.log"


def set_debug_level(debug: bool):
    if debug:
        for logger in LogConfig["loggers"].values():
            logger["level"] = "DEBUG"


if __name__ == "__main__":
    logger = get_logger()

    logger.debug("hello world")
    logger.info("hello world")
    logger.warning("hello world")

    try:
        logger.error("hello world")
        raise EOFError("EOF!")
    except EOFError:
        logger.critical("CRITICAL MESSAGE", exc_info=True)

    try:
        raise EOFError("EOF!")
    except Exception:
        logger.exception("hello world")
