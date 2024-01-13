from functools import lru_cache
from typing import Any
import logging
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


@lru_cache
def get_settings():
    return _Settings()


class LoggerSettings(BaseSettings):
    LOG_FILE: str
    LOG_LEVEL_FILE: str
    LOG_LEVEL_CONSOLE: str
    LOG_FORMAT_FILE: str
    LOG_FORMAT_CONSOLE: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    def __init__(self, **values: Any):
        super().__init__(**values)
        logger.setLevel(logging.DEBUG)
        self._add_console_handler()
        self._add_file_handler()

    def _add_file_handler(self):
        file_handler = logging.FileHandler(self.LOG_FILE)
        file_handler.setLevel(self.LOG_LEVEL_FILE)
        file_formatter = logging.Formatter(self.LOG_FORMAT_FILE)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    def _add_console_handler(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.LOG_LEVEL_CONSOLE)
        console_formatter = logging.Formatter(self.LOG_FORMAT_CONSOLE)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)


class ExtractorSettings(BaseSettings):
    BATCH_SIZE: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        env_prefix='EXTRACTOR_',
    )


class LoaderSettings(BaseSettings):
    ELASTIC_HOST: str
    ELASTIC_PORT: str
    INDEX_NAME: str
    BATCH_SIZE: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        env_prefix='LOADER_',
    )


class _Settings(BaseSettings):
    logger: LoggerSettings = LoggerSettings()
    extractor: ExtractorSettings = ExtractorSettings()
    loader: LoaderSettings = LoaderSettings()
    PG_DSN: PostgresDsn
    TABLE_NAMES: tuple

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )
