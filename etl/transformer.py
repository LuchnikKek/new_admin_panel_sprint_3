from collections import defaultdict
from typing import Any

from configs import logger


class Transformer:
    def collapse_data(self, film_works: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged_data = defaultdict(
            lambda: {
                'uuid': None,
                'title': None,
                'description': None,
                'imdb_rate': None,
                'p_info': set(),
                'genre_name': set(),
            }
        )

        for item in film_works:
            (
                uuid,
                title,
                description,
                imdb_rate,
                p_role,
                p_uuid,
                p_name,
                genre_name,
            ) = item
            merged_data[uuid]['uuid'] = uuid
            merged_data[uuid]['title'] = title
            merged_data[uuid]['description'] = description
            merged_data[uuid]['imdb_rate'] = imdb_rate
            merged_data[uuid]['p_info'].add((p_role, p_uuid, p_name))
            merged_data[uuid]['genre_name'].add(genre_name)

        result = [
            {
                'uuid': v['uuid'],
                'title': v['title'],
                'description': v['description'],
                'imdb_rate': v['imdb_rate'],
                'p_info': tuple(v['p_info']),
                'genre_name': tuple(v['genre_name']),
            }
            for v in merged_data.values()
        ]
        logger.info(
            f'{self.__class__.__name__}: сжаты до количества {len(result)} записей.'
        )
        return result

    def prepare_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        prepared_data = []
        for record in data:  # todo ого, откуда он так хорошо знает название индекса?
            service_dict = {'index': {'_index': 'movies', '_id': record['uuid']}}
            data_dict = {
                'id': record['uuid'],
                'imdb_rating': record['imdb_rate'],
                'genre': list(record['genre_name']),
                'title': record['title'],
                'description': record['description'],
                'director': next(
                    (info[1] for info in record['p_info'] if info[0] == 'director'),
                    None,
                ),
                'actors_names': [
                    info[1] for info in record['p_info'] if info[0] == 'actor'
                ],
                'writers_names': [
                    info[1] for info in record['p_info'] if info[0] == 'writer'
                ],
                'actors': [
                    {'id': info[2], 'name': info[1]}
                    for info in record['p_info']
                    if info[0] == 'actor'
                ],
                'writers': [
                    {'id': info[2], 'name': info[1]}
                    for info in record['p_info']
                    if info[0] == 'writer'
                ],
            }
            prepared_data.extend([service_dict, data_dict])
        logger.info(
            f'{self.__class__.__name__}: подготовлено {len(prepared_data)//2} записей.'
        )
        return prepared_data
