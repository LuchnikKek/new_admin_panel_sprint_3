import psycopg2

from configs import get_settings
from etl import ETL

if __name__ == '__main__':
    settings = get_settings()
    dsn = settings.PG_DSN
    try:
        with psycopg2.connect(dsn=str(dsn)) as pg_connection:
            etl = ETL(settings=settings, pg_connection=pg_connection)
            etl.start_loop(table_names=settings.TABLE_NAMES)
    finally:
        pg_connection.close()
