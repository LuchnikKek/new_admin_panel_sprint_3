from typing import Any, Union
import time
from psycopg2.extensions import connection as _connection
from configs import _Settings
from loader import Loader
from transformer import Transformer
from extractor import Extractor


class ETL:
    def __init__(self, settings: _Settings, pg_connection: _connection):
        self.extractor = Extractor(
            connection=pg_connection, settings=settings.extractor
        )
        self.transformer = Transformer()
        self.loader = Loader(settings=settings.loader)
        self.settings = settings

    def extract_data(self, table_name: str) -> Union[list[dict[str, Any]], list]:
        modified_records = self.extractor.run(table_name=table_name)
        return modified_records

    def transform_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        collapsed_data = self.transformer.collapse_data(data)
        prepared_data = self.transformer.prepare_data(collapsed_data)
        return prepared_data

    def load_data(self, data: list[dict[str, Any]]) -> list[dict]:
        result = self.loader.load_data(data)
        return result

    def start_loop(self, table_names: list[str]) -> None:
        while True:
            for table_name in table_names:
                extracted = self.extract_data(table_name)
                transformed = self.transform_data(extracted)
                self.load_data(transformed)
            time.sleep(self.settings.LOOP_PAUSE_SEC)
