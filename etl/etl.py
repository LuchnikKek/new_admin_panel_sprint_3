import psycopg2

from configs import get_settings
from loader import Loader
from transformer import Transformer
from extractor import Extractor


if __name__ == '__main__':
    settings = get_settings()
    dsn = str(settings.PG_DSN)

    try:
        with psycopg2.connect(dsn=dsn) as pg_connection:
            extractor = Extractor(connection=pg_connection, settings=settings.extractor)
            transformer = Transformer()
            loader = Loader(settings=settings.loader)

            while True:
                modified_data = extractor.run(settings.TABLE_NAMES)

                collapsed_data = transformer.collapse_data(modified_data)
                prepared_data = transformer.prepare_data(collapsed_data)

                loader.load(prepared_data=prepared_data)
    finally:
        pg_connection.close()
