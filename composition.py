'''Модуль с классом композиции.'''
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Composition:
    """Класс композиции."""
    title: str
    artist: str
    file_path: Path

    def __str__(self) -> str:
        return(f"{self.artist} -- {self.title}")
