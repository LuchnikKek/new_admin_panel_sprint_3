import psycopg2
from elasticsearch import Elasticsearch
from psycopg2.extras import DictCursor

from configs import get_settings
from etl import ETL

if __name__ == '__main__':
    settings = get_settings()
    pg_dsn = settings.PG_DSN
    es_host = f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'
    try:
        with (
            psycopg2.connect(
                dsn=str(pg_dsn), cursor_factory=DictCursor
            ) as pg_connection,
            Elasticsearch(es_host) as es_connection,
        ):
            etl = ETL(
                settings=settings,
                pg_connection=pg_connection,
                es_connection=es_connection,
            )
            etl.start_loop(table_names=settings.TABLE_NAMES)
    finally:
        pg_connection.close()
