from typing import Any

from storages import BaseStorage


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        current_state = self.storage.retrieve_state()
        current_state[key] = value
        self.storage.save_state(current_state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        current_state = self.storage.retrieve_state()
        return current_state.get(key)
