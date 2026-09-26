"""GUI плеера на PyQt5."""
import os
import sys

import pygame

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QComboBox, QLabel,
    QMessageBox, QInputDialog, QFileDialog,
)

from play_list import PlayList
from composition import Composition


class PlayerWindow(QMainWindow):
    """Главное окно плеера."""

    def __init__(self) -> None:
        """Инициализация окна."""

        super().__init__()
        self.setWindowTitle("Simple MP")
        self.resize(700, 500)

        self.playlists: dict = {}
        self.current_playlist_name: str | None = None

        self._build_ui()
        self._connect_signals()
        self._init_pygame()

    def _build_ui(self) -> None:
        """Собрать интерфейс."""
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        playlist_row = QHBoxLayout()
        playlist_row.addWidget(QLabel("Плейлист:"))
        self.playlist_combo = QComboBox()
        playlist_row.addWidget(self.playlist_combo, stretch=1)
        self.btn_create_playlist = QPushButton("+ Плейлист")
        self.btn_delete_playlist = QPushButton("- Плейлист")
        playlist_row.addWidget(self.btn_create_playlist)
        playlist_row.addWidget(self.btn_delete_playlist)
        root.addLayout(playlist_row)

        self.track_list = QListWidget()
        root.addWidget(self.track_list, stretch=1)

        track_row = QHBoxLayout()
        self.btn_add_track = QPushButton("+ Трек")
        self.btn_remove_track = QPushButton("- Трек")
        self.btn_move_up = QPushButton("↑ Вверх")
        self.btn_move_down = QPushButton("↓ Вниз")
        track_row.addWidget(self.btn_add_track)
        track_row.addWidget(self.btn_remove_track)
        track_row.addWidget(self.btn_move_up)
        track_row.addWidget(self.btn_move_down)
        track_row.addStretch()
        root.addLayout(track_row)

        play_row = QHBoxLayout()
        self.btn_prev = QPushButton("<|<|")
        self.btn_play = QPushButton("|>")
        self.btn_next = QPushButton("|>|>")
        self.btn_stop = QPushButton("||")
        play_row.addWidget(self.btn_prev)
        play_row.addWidget(self.btn_play)
        play_row.addWidget(self.btn_next)
        play_row.addWidget(self.btn_stop)
        play_row.addStretch()
        root.addLayout(play_row)

        self.status_label = QLabel("Ничего не играет")
        self.status_label.setAlignment(Qt.AlignCenter)
        root.addWidget(self.status_label)

    def _init_pygame(self) -> None:
        """Инициализировать pygame и таймер для автоперехода."""
        pygame.display.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_pygame_events)
        self.timer.start(200)

    def _check_pygame_events(self) -> None:
        """Проверить события pygame (окончание трека)."""
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self._on_next()

    def _on_create_playlist(self) -> None:
        """Создать новый плейлист."""
        name, ok = QInputDialog.getText(self, "Новый плейлист", "Имя:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self.playlists:
            QMessageBox.warning(self, "Ошибка", "Плейлист с таким именем уже есть")
            return
        self.playlists[name] = PlayList()
        self._refresh_playlist_selector()
        self.playlist_combo.setCurrentText(name)

    def _on_delete_playlist(self) -> None:
        """Удалить текущий плейлист."""
        name = self.playlist_combo.currentText()
        if not name:
            return
        reply = QMessageBox.question(
            self, "Удалить плейлист?",
            f"Удалить плейлист «{name}»?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        playlist = self.playlists[name]
        if playlist.current is not None:
            playlist.stop()
            self.status_label.setText("Ничего не играет")

        del self.playlists[name]
        self._refresh_playlist_selector()

    def _refresh_playlist_selector(self) -> None:
        """Обновить выпадающий список плейлистов."""
        self.playlist_combo.blockSignals(True)
        current = self.playlist_combo.currentText()
        self.playlist_combo.clear()
        self.playlist_combo.addItems(list(self.playlists.keys()))
        if current in self.playlists:
            self.playlist_combo.setCurrentText(current)
        self.playlist_combo.blockSignals(False)
        self._on_playlist_selected()

    def _on_playlist_selected(self) -> None:
        """Сменить активный плейлист."""
        self.current_playlist_name = self.playlist_combo.currentText() or None
        self._refresh_track_list()

    def current_playlist(self) -> PlayList | None:
        """Хелпер: текущий плейлист или None."""
        if self.current_playlist_name is None:
            return None
        return self.playlists.get(self.current_playlist_name)

    def _refresh_track_list(self) -> None:
        """Обновить QListWidget по текущему плейлисту."""
        self.track_list.clear()
        pl = self.current_playlist()
        if pl is None:
            return
        for node in pl:
            comp = node.data
            self.track_list.addItem(str(comp))

    def _on_add_track(self) -> None:
        """Добавить трек в текущий плейлист."""
        pl = self.current_playlist()
        if pl is None:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте плейлист")
            return

        title, ok = QInputDialog.getText(self, "Новый трек", "Название:")
        if not ok or not title.strip():
            return
        artist, ok = QInputDialog.getText(self, "Новый трек", "Исполнитель:")
        if not ok:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите аудиофайл", "",
            "Аудио (*.mp3 *.ogg *.wav)",
        )
        if not file_path:
            return

        comp = Composition(title.strip(), artist.strip(), file_path)
        pl.append(comp)
        self._refresh_track_list()

    def _on_remove_track(self) -> None:
        """Удалить выбранный трек."""
        pl = self.current_playlist()
        if pl is None:
            return
        row = self.track_list.currentRow()
        if row < 0:
            return
        comp = pl[row]
        pl.remove(comp)
        self._refresh_track_list()

    def _on_move_up(self) -> None:
        """Переместить трек на позицию выше."""
        self._move_track(-1)

    def _on_move_down(self) -> None:
        """Переместить трек на позицию ниже."""
        self._move_track(+1)

    def _move_track(self, direction: int) -> None:
        """Переместить выбранный трек на direction позиций."""
        pl = self.current_playlist()
        if pl is None:
            return
        row = self.track_list.currentRow()
        new_row = row + direction
        if row < 0 or new_row < 0 or new_row >= len(pl):
            return

        items = [pl[i] for i in range(len(pl))]
        items[row], items[new_row] = items[new_row], items[row]

        self._rebuild_playlist(pl, items)

        self._refresh_track_list()
        self.track_list.setCurrentRow(new_row)

    @staticmethod
    def _rebuild_playlist(pl: PlayList, items: list) -> None:
        """Пересобрать плейлист в новом порядке."""
        while len(pl) > 0:
            pl.remove(pl[0])
        for comp in items:
            pl.append(comp)

    def on_play(self) -> None:
        """Играть выбранный трек."""
        pl = self.current_playlist()
        if pl is None:
            return
        row = self.track_list.currentRow()
        if row < 0:
            return
        comp = pl[row]
        pl.play_all(comp)
        self._update_now_playing()

    def _on_next(self) -> None:
        """Следующий трек."""
        pl = self.current_playlist()
        if pl is None:
            return
        pl.next_track()
        self._highlight_current()

    def _on_previous(self) -> None:
        """Предыдущий трек."""
        pl = self.current_playlist()
        if pl is None:
            return
        pl.previous_track()
        self._highlight_current()

    def _on_stop(self) -> None:
        """Остановить воспроизведение."""
        pl = self.current_playlist()
        if pl is not None:
            pl.stop()
        self.status_label.setText("Ничего не играет")

    def _highlight_current(self) -> None:
        """Подсветить текущий играющий трек в списке."""
        pl = self.current_playlist()
        if pl is None:
            return
        current = pl.current
        if current is None:
            return
        for i in range(self.track_list.count()):
            if pl[i] == current:
                self.track_list.setCurrentRow(i)
                break
        self._update_now_playing()

    def _update_now_playing(self) -> None:
        """Обновить надпись «сейчас играет»."""
        pl = self.current_playlist()
        if pl is None or pl.current is None:
            self.status_label.setText("Ничего не играет")
            return
        self.status_label.setText(f"Сейчас играет: {pl.current}")

    def _connect_signals(self) -> None:
        """Подключить сигналы кнопок."""
        self.btn_create_playlist.clicked.connect(self._on_create_playlist)
        self.btn_delete_playlist.clicked.connect(self._on_delete_playlist)
        self.playlist_combo.currentIndexChanged.connect(self._on_playlist_selected)

        self.btn_add_track.clicked.connect(self._on_add_track)
        self.btn_remove_track.clicked.connect(self._on_remove_track)
        self.btn_move_up.clicked.connect(self._on_move_up)
        self.btn_move_down.clicked.connect(self._on_move_down)

        self.btn_play.clicked.connect(self._on_play)
        self.btn_next.clicked.connect(self._on_next)
        self.btn_prev.clicked.connect(self._on_previous)
        self.btn_stop.clicked.connect(self._on_stop)

        self.track_list.itemDoubleClicked.connect(
            lambda _item: self._on_play()
        )

def main() -> None:
    """Точка входа."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    app = QApplication(sys.argv)
    window = PlayerWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
