object_ids_with_modified_field_gt_query = """
    SELECT id, modified
    FROM content.{table_name}
    WHERE modified > '{modified_timestamp}'
    ORDER BY modified
    LIMIT {batch_size};
"""

filmworks_ids_related_to_object_ids_query = """
    SELECT fw.id
    FROM content.film_work fw
    LEFT JOIN content.{table_name}_film_work pfw ON pfw.film_work_id = fw.id
    WHERE pfw.{table_name}_id IN ({object_ids})
    ORDER BY fw.modified; 
"""


full_film_works_by_ids = """
    SELECT
        fw.id as fw_id, 
        fw.title, 
        fw.description, 
        fw.rating,
        pfw.role, 
        p.full_name,
        p.id, 
        g.name
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.id IN ({film_works_ids}); 
"""