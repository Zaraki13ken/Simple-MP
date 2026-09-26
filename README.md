# Simple MP

Практическая работа №1: связные списки.

GUI-плеер на PyQt5 с кольцевым двусвязным списком композиций.

## Возможности

- Создание и удаление плейлистов (несколько)
- Добавление и удаление треков
- Перемещение треков вверх / вниз
- Воспроизведение, пауза, остановка
- Переход к следующему / предыдущему треку
- Автопереход по кольцу: после последнего трека играет первый

## Стек

- Python 3.10+
- PyQt5 — интерфейс
- pygame — воспроизведение аудио

## Установка
- **Windows**
    ```bash
    git clone https://github.com/ТВОЙ_НИК/simple-mp.git
    cd simple-mp
    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
    ```
- **Linux/macOS**
    ```bash
    git clone https://github.com/ТВОЙ_НИК/simple-mp.git
    cd simple-mp
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Запуск

```bash 
python player_gui.py
```