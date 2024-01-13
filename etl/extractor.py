import datetime
from typing import Tuple

import psycopg2.extensions
from psycopg2.extensions import connection as _connection

from configs import ExtractorSettings
from configs import logger
from queries import (
    object_ids_with_modified_field_gt_query,
    filmworks_ids_related_to_object_ids_query,
    full_film_works_by_ids,
)


class Producer:
    def __init__(self, connection: _connection):
        self.connection = connection
        self.query = object_ids_with_modified_field_gt_query

    def extract(
        self,
        table_name: str,
        modified_timestamp: datetime.datetime,
        batch_size: int,
    ) -> tuple[list[str], datetime]:
        cursor: psycopg2.extensions.cursor = self.connection.cursor()
        query = self.query.format(
            table_name=table_name,
            modified_timestamp=modified_timestamp,
            batch_size=batch_size,
        )
        cursor.execute(query=query)
        result = cursor.fetchmany(size=batch_size)

        last_date_in_result = result[-1][1] if result else None
        result = [el[0] for el in result]

        logger.info(f'{self.__class__}: получено {len(result)} записей.')
        return result, last_date_in_result


class Enricher:
    def __init__(self, connection: _connection):
        self.connection = connection
        self.query = filmworks_ids_related_to_object_ids_query

    def extract(self, table_name: str, object_ids: list[str]) -> list[str]:
        if table_name == 'film_work':
            return object_ids
        cursor: psycopg2.extensions.cursor = self.connection.cursor()
        query = self.query.format(
            table_name=table_name,
            object_ids=", ".join(['\'' + obj_id + '\'' for obj_id in object_ids]),
        )
        cursor.execute(query=query)
        result = cursor.fetchall()
        result = self._transform_result(result)
        logger.info(f'{self.__class__}: получено {len(result)} записей.')
        return result

    @staticmethod
    def _transform_result(result: list[Tuple[str,]]) -> list[str,]:
        return [res[0] for res in result]


class Merger:
    def __init__(self, connection: _connection):
        self.connection = connection
        self.query = full_film_works_by_ids

    def extract(self, film_work_ids: list[str]) -> list[str]:
        cursor: psycopg2.extensions.cursor = self.connection.cursor()
        query = self.query.format(
            film_works_ids=", ".join(['\'' + fw_id + '\'' for fw_id in film_work_ids]),
        )
        cursor.execute(query=query)
        result = cursor.fetchall()
        logger.info(f'{self.__class__}: получено {len(result)} записей.')
        return result


class Extractor:
    def __init__(self, connection: _connection, settings: ExtractorSettings):
        self.connection = connection
        self.settings = settings
        self.producer = Producer(self.connection)
        self.enricher = Enricher(self.connection)
        self.merger = Merger(self.connection)
        self.last_extracted_datetime: datetime.datetime = datetime.datetime(1970, 1, 1)

    def run(self, table_names: list[str]):
        for table in table_names:
            modified_objs_ids, self.last_extracted_datetime = self.producer.extract(
                table_name=table,
                batch_size=self.settings.BATCH_SIZE,
                modified_timestamp=self.last_extracted_datetime,
            )
            related_filmworks_ids = self.enricher.extract(
                table_name=table, object_ids=modified_objs_ids
            )
            related_filmworks_data = self.merger.extract(
                film_work_ids=related_filmworks_ids
            )
            return related_filmworks_data
