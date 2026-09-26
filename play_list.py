"""Модуль плейлиста с воспроизведением композиций."""

import pygame
from composition import Composition
from linked_list import LinkedList, LinkedListItem


class PlayList(LinkedList):
    """Плейлист — кольцевой список композиций с указателем на текущую."""

    def __init__(self) -> None:
        """Инициализация пустого плейлиста."""
        super().__init__()
        self._current_item: LinkedListItem | None = None

    @property
    def current(self) -> Composition | None:
        """Текущая композиция или None, если ничего не играет."""
        if self._current_item is None:
            return None
        return self._current_item.data

    def play_all(self, item: Composition) -> None:
        """Начать воспроизведение всех треков с указанной композиции."""
        node = self._find(item)
        if node is None:
            raise ValueError(f"Композиция {item!r} отсутствует в плейлисте")
        self._current_item = node
        self._play_current()

    def next_track(self) -> Composition | None:
        """Перейти к следующему треку."""
        if self._current_item is None:
            return None
        self._current_item = self._current_item.next_item
        self._play_current()
        return self.current

    def previous_track(self) -> Composition | None:
        """Перейти к предыдущему треку."""
        if self._current_item is None:
            return None
        self._current_item = self._current_item.previous_item
        self._play_current()
        return self.current

    def _play_current(self) -> None:
        """Воспроизвести текущую композицию."""
        if self.current is None:
            return
        pygame.mixer.music.load(self.current.file_path)
        pygame.mixer.music.play()

    def stop(self) -> None:
        """Остановить воспроизведение."""
        pygame.mixer.music.stop()
        self._current_item = None

    @staticmethod
    def pause() -> None:
        """Поставить на паузу."""
        pygame.mixer.music.pause()

    @staticmethod
    def unpause() -> None:
        """Снять с паузы."""
        pygame.mixer.music.unpause()
