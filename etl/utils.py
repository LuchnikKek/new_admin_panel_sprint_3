def list_to_sql_array_string(some_list: list) -> str:
    """
    Usage:
        [1, 2, '3'] -> "('1', '2', '3')"
    """
    return '(' + ", ".join(['\'' + el + '\'' for el in some_list]) + ')'
