"""
Модуль содержащий класс связного списка
и класс узла связного списка
"""
from __future__ import annotations
from typing import Any, Iterator


class LinkedListItem:
    """Узел связного списка"""
    def __init__(self, data: Any = None) -> None:
        self._data = data
        self._previous: LinkedListItem | None = None
        self._next: LinkedListItem | None = None

    @property
    def data(self) -> Any:
        """Данные узла."""
        return self._data

    @property
    def next_item(self) -> LinkedListItem | None:
        """Следующий элемент"""
        return self._next

    @next_item.setter
    def next_item(self, value: LinkedListItem | None) -> None:
        self._next = value
        if value is not None and value.previous_item is not self:
            value.previous_item = self

    @property
    def previous_item(self) -> LinkedListItem | None:
        """Предыдущий элемент"""
        return self._previous

    @previous_item.setter
    def previous_item(self, value: LinkedListItem | None) -> None:
        self._previous = value
        if value is not None and value.next_item is not self:
            value.next_item = self

    def __repr__(self) -> str:
        return f"LinkedListItem({self._data!r})"


class LinkedList:
    """Кольцевой двусвязный список."""
    def __init__(self, first_item: LinkedListItem | None = None) -> None:
        self._first_item = first_item
        self._size = 0
        if first_item is not None:
            node = first_item
            while True:
                self._size += 1
                node = node.next_item
                if node is first_item:
                    break

    @property
    def first_item(self) -> LinkedListItem | None:
        """Первый элемент списка."""
        return self._first_item

    @property
    def last(self) -> LinkedListItem | None:
        """Последний элемент списка."""
        if self._first_item is None:
            return None
        return self._first_item.previous_item

    def append_left(self, item: Any) -> None:
        """Добавить данные в начало списка."""
        node = LinkedListItem(item)
        if self._first_item is None:
            node.next_item = node
            self._first_item = node
        else:
            last = self._first_item.previous_item
            node.next_item = self._first_item
            last.next_item = node
            self._first_item = node
        self._size += 1

    def append_right(self, item: Any) -> None:
        """Добавить данные в конец списка."""
        if self._first_item is None:
            self.append_left(item)
            return
        node = LinkedListItem(item)
        last = self._first_item.previous_item
        last.next_item = node
        node.next_item = self._first_item
        self._size += 1

    def append(self, item: Any) -> None:
        """Алиас append_right."""
        self.append_right(item)

    def remove(self, item: Any) -> None:
        """Удалить первое вхождение данных."""
        node = self._find(item)
        if node is None:
            raise ValueError(f"{item!r} отсутствует в списке")
        if self._size == 1:
            self._first_item = None
        else:
            prev = node.previous_item
            nxt = node.next_item
            prev.next_item = nxt
            if node is self._first_item:
                self._first_item = nxt
        node.next_item = None
        node.previous_item = None
        self._size -= 1

    def insert(self, previous: Any, item: Any) -> None:
        """Вставить данные item после узла с данными previous."""
        node = self._find(previous)
        if node is None:
            raise ValueError(f"{previous!r} отсутствует в списке")
        new_node = LinkedListItem(item)
        after = node.next_item
        node.next_item = new_node
        new_node.next_item = after
        self._size += 1

    def _find(self, item: Any) -> LinkedListItem | None:
        for node in self._iter_nodes():
            if node.data == item:
                return node
        return None

    def _iter_nodes(self) -> Iterator[LinkedListItem]:
        if self._first_item is None:
            return
        node = self._first_item
        for _ in range(self._size):
            yield node
            node = node.next_item

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        return self._iter_nodes()

    def __getitem__(self, index: int) -> Any:
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError("Индекс вне диапазона")
        node = self._first_item
        for _ in range(index):
            node = node.next_item
        return node.data

    def __contains__(self, item: Any) -> bool:
        return self._find(item) is not None

    def __reversed__(self) -> Iterator[Any]:
        if self._first_item is None:
            return
        node = self.last
        for _ in range(self._size):
            yield node.data
            node = node.previous_item
