from typing import Any

from elasticsearch import Elasticsearch

from configs import LoaderSettings, logger


class Loader:
    def __init__(self, settings: LoaderSettings):
        self.settings = settings
        self.es_connection = Elasticsearch(
            f'http://{self.settings.ELASTIC_HOST}:{self.settings.ELASTIC_PORT}'
        )

    def load(self, prepared_data: list[dict[str, Any]]):
        # для каждой строки даты по одной служебной
        batch_size = self.settings.BATCH_SIZE * 2
        for i in range(0, len(prepared_data), batch_size):
            self._bulk_to_elastic(prepared_data[i : i + batch_size])
        logger.info(
            f'{self.__class__}: все {len(prepared_data)} записей сохранены в ES.'
        )

    def _bulk_to_elastic(self, prepared_data):
        # todo: а он по идее должен знать название
        res = self.es_connection.bulk(
            index='movies',
            body=prepared_data,
            refresh=True,
            filter_path='items.*.error',
        )
        if res == {}:
            logger.info(
                f'{self.__class__}: в хранилище сохранено {len(prepared_data)} записей.'
            )
        else:
            logger.error(
                f'{self.__class__}: сохранение {len(prepared_data)} записей не удалось.'
            )
