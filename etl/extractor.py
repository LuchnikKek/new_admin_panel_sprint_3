from datetime import datetime
from typing import Optional, Union, Any

import backoff
import psycopg2
from psycopg2.extensions import connection as _connection

from configs import ExtractorSettings
from configs import logger
from exceptions import EndOfDataException
from queries import (
    object_ids_with_modified_field_gt_query,
    film_works_ids_related_to_object_ids_query,
    full_film_works_by_ids,
)
from state import State
from storages import JsonFileStorage
from utils import list_to_sql_array_string


class BaseSQLExtractor:
    def __init__(self, connection: _connection, query: str, name: str):
        self.name = name
        self.connection = connection
        self.query = query
        self._storage = JsonFileStorage('./storages/' + self.name)
        self.state = State(storage=self._storage)
        self.unused_data = self.state.get_state('unused_data')
        self.state.set_state('unused_data', {})

    @staticmethod
    def _save_state(e):
        stated_data = e['kwargs']
        entity = e['args'][0]
        entity.state.set_state(key='unused_data', value=stated_data)
        logger.error(f'При работе возникла ошибка. Состояние сохранено.')

    @backoff.on_exception(
        exception=Exception,
        wait_gen=backoff.expo,
        max_tries=1,
        on_giveup=_save_state,  # noqa
    )
    @backoff.on_exception(
        exception=psycopg2.OperationalError, wait_gen=backoff.expo, max_tries=5
    )
    def extract(self, **query_params):
        query = self.query.format(**query_params)
        with self.connection.cursor() as curs:
            curs.execute(query=query)
            result = curs.fetchall()

        logger.info(f'{self.name}: получено {len(result)} записей.')
        return result


class Extractor:
    def __init__(self, connection: _connection, settings: ExtractorSettings):
        self.settings = settings
        self.connection = connection
        self._storage = JsonFileStorage('./storages/' + self.__class__.__name__)
        self.state = State(storage=self._storage)
        self.last_extracted_datetime_str: Optional[datetime] = (
            datetime.strptime(
                self.state.get_state('last_extracted_datetime'),
                '%Y-%m-%d %H:%M:%S.%f%z',
            )
            if self.state.get_state('last_extracted_datetime') is not None
            else datetime.min
        )
        self.Producer = BaseSQLExtractor(connection=self.connection, query=object_ids_with_modified_field_gt_query, name='Producer')  # fmt: skip
        self.Enricher = BaseSQLExtractor(connection=self.connection, query=film_works_ids_related_to_object_ids_query, name='Enricher')  # fmt: skip
        self.Merger = BaseSQLExtractor(connection=self.connection, query=full_film_works_by_ids, name='Merger')  # fmt: skip

    def produce_data(self, table_name: str) -> list[str,]:
        modified_records = self.Producer.extract(
            table_name=table_name,
            batch_size=self.settings.BATCH_SIZE,
            modified_timestamp=self.last_extracted_datetime_str,
        )
        if not modified_records:
            self.last_extracted_datetime_str = datetime.min
            raise EndOfDataException
        last_extracted_datetime = modified_records[-1]['modified']
        self.last_extracted_datetime_str = last_extracted_datetime.strftime(
            '%Y-%m-%d %H:%M:%S.%f%z'
        )
        self.state.set_state(
            'last_extracted_datetime', self.last_extracted_datetime_str
        )
        modified_records_ids = [rec['id'] for rec in modified_records]
        return modified_records_ids

    def enrich_data(
        self, table_name: str, modified_records_ids: Union[list[str] | str]
    ) -> list[str,]:
        if table_name == 'film_work':
            return modified_records_ids
        modified_records_ids_string = list_to_sql_array_string(modified_records_ids)
        related_film_works = self.Enricher.extract(
            table_name=table_name, modified_records_ids=modified_records_ids_string
        )
        related_film_work_ids = [fw['id'] for fw in related_film_works]
        return related_film_work_ids

    def merge_data(
        self, film_works_ids: Union[list[str] | str]
    ) -> list[dict[str, Any]]:
        film_works_ids_str = list_to_sql_array_string(film_works_ids)
        related_film_works_data = self.Merger.extract(film_works_ids=film_works_ids_str)
        return related_film_works_data

    def run(self, table_name: str):
        modified_records_ids = self.produce_data(table_name=table_name)
        related_film_works_ids = self.enrich_data(
            table_name=table_name, modified_records_ids=modified_records_ids
        )
        related_film_works_data = self.merge_data(film_works_ids=related_film_works_ids)
        return related_film_works_data

    def check_for_unused_data(self) -> bool:
        return (
            self.Producer.unused_data
            or self.Enricher.unused_data
            or self.Merger.unused_data
        )

    def unused_data(self) -> list[dict[str, Any]]:
        unused_data = []
        if self.Merger.unused_data:
            unused_data.extend(self.merge_data(**self.Merger.unused_data))
            self.Merger.unused_data = {}
        if self.Enricher.unused_data:
            enriched_data = self.enrich_data(**self.Enricher.unused_data)
            self.Enricher.unused_data = {}
            unused_data.extend(self.merge_data(enriched_data))
        return unused_data
