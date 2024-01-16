import time
from itertools import cycle
from typing import Any, Union

from psycopg2.extensions import connection as _connection

from configs import _Settings
from exceptions import EndOfDataException
from extractor import Extractor
from loader import Loader
from transformer import Transformer


class ETL:
    def __init__(self, settings: _Settings, pg_connection: _connection, es_connection):
        self.extractor = Extractor(
            connection=pg_connection, settings=settings.extractor
        )
        self.transformer = Transformer()
        self.loader = Loader(settings=settings.loader, connection=es_connection)
        self.settings = settings

    def extract_data(self, table_name: str) -> Union[list[dict[str, Any]], list]:
        if self.extractor.check_for_unused_data():
            return self.extractor.unused_data()
        else:
            return self.extractor.run(table_name=table_name)

    def transform_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        collapsed_data = self.transformer.collapse_data(data)
        prepared_data = self.transformer.prepare_data(collapsed_data)
        return prepared_data

    def load_data(self, data: list[dict[str, Any]]) -> list[dict]:
        result = self.loader.load_data(data)
        return result

    def start_loop(self, table_names: list[str]) -> None:
        for table_name in cycle(table_names):
            try:
                extracted = self.extract_data(table_name)
            except EndOfDataException:
                continue
            transformed = self.transform_data(extracted)
            self.load_data(transformed)
            time.sleep(self.settings.LOOP_PAUSE_SEC)
