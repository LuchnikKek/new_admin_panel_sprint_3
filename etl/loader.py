from typing import Any

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch

from configs import LoaderSettings, logger


class Loader:
    def __init__(self, settings: LoaderSettings):
        self.settings = settings
        self.es_connection = Elasticsearch(
            f'http://{self.settings.ELASTIC_HOST}:{self.settings.ELASTIC_PORT}'
        )

    def load_data(self, prepared_data: list[dict[str, Any]]) -> list[ObjectApiResponse]:
        # для каждой строки даты по одной служебной
        batch_size = self.settings.BATCH_SIZE * 2
        data_length = len(prepared_data) // 2
        result = [
            self._bulk_to_elastic(prepared_data[i : i + batch_size])
            for i in range(0, len(prepared_data), batch_size)
        ]
        logger.info(
            f'{self.__class__}: {data_length - len(result) + 1}/{data_length} записей сохранены в ElasticSearch.'
        )
        return result

    def _bulk_to_elastic(self, prepared_data) -> ObjectApiResponse:
        # todo: а он по идее должен знать название индекса
        res = self.es_connection.bulk(
            index='movies',
            body=prepared_data,
            refresh=True,
            filter_path='items.*.error',
        )
        if res.body:
            logger.error(
                f'{self.__class__}: ошибка при сохранении в Elastic: {res.body}'
            )
        else:
            return res
