from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from typing import DefaultDict


if getattr(sys, 'frozen', False):
    # Если приложение запущено через PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
    progress_file = os.path.join(BASE_DIR, 'morse_progress.json')
else:
    # Если приложение запущено через python
    # basedir = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    progress_file = BASE_DIR / 'morse_progress.json'


@dataclass
class Level:
    current_level: int = 1
    last_level: int = 1
    user_progress:  DefaultDict[str, DefaultDict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {'total': 0, 'correct': 0}))
    last_level_progress: DefaultDict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {'total': 0, 'correct': 0}))
    last_saved: str = datetime.now().isoformat()
    level_progress: DefaultDict[str, DefaultDict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {'total': 0, 'correct': 0}))


def save_progress(level: Level):
    """Сохранение прогресса пользователя"""

    data = {
        'current_level': level.current_level,
        'last_level': level.last_level,
        'user_progress': level.user_progress,
        'last_level_progress': level.last_level_progress,
        'last_saved': datetime.now().isoformat()
    }
    with open(progress_file, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=2)


def load_progress(level: Level):
    """Загрузка прогресса пользователя"""
    try:
        with open(progress_file, 'r', encoding='utf8') as f:
            data = json.load(f)
            level.current_level = data.get('current_level', level.current_level)
            level.last_level = data.get('last_level', level.last_level)
            level.user_progress = defaultdict(
                    lambda: {'total': 0, 'correct': 0},
                    data.get('user_progress', {})
                )
            level.last_level_progress = defaultdict(
                    lambda: {'total': 0, 'correct': 0},
                    data.get('last_level_progress', {})
                )
    except FileNotFoundError:
        level.user_progress = defaultdict(lambda: {'total': 0, 'correct': 0})

    return level