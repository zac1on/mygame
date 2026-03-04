# settings.py
import json
import os
import pygame

# Инициализация pygame для получения информации о мониторе
pygame.init()

# Получаем разрешение монитора пользователя
_display_info = pygame.display.Info()
NATIVE_WIDTH = _display_info.current_w
NATIVE_HEIGHT = _display_info.current_h

# Экран (начальные значения)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "RPG Adventure"

# Тайлы
TILE_SIZE = 64

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 215, 0)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
BROWN = (139, 90, 43)
DARK_GREEN = (34, 100, 34)
DARK_BLUE = (20, 20, 80)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (150, 50, 200)

# Игрок
PLAYER_SPEED = 4
PLAYER_MAX_HP = 100
PLAYER_MAX_MANA = 50
PLAYER_BASE_ATTACK = 10
PLAYER_BASE_DEFENSE = 5

# Карта (увеличенная для больших разрешений)
GAME_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
     1, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0,
     0, 1],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0,
     0, 1],
    [1, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1, 1, 1, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0,
     0, 1],
    [1, 0, 4, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0,
     0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 4, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
     1, 1],
]

# NPC
NPC_DATA = [
    (12, 4, "Старейшина", [
        "Добро пожаловать, герой!",
        "Наше село атакуют слизни.",
        "Убей 3 слизней и вернись ко мне.",
    ], "kill_slimes"),
    (4, 13, "Кузнец", [
        "Я кузнец этой деревни.",
        "Принеси мне 2 руды, и я выкую меч.",
    ], "bring_ore"),
    (23, 14, "Торговец", [
        "Хочешь купить зелье?",
        "У меня лучшие цены в округе!",
    ], None),
]

# Враги
ENEMY_DATA = [
    (8, 2, "slime"),
    (18, 3, "slime"),
    (6, 8, "slime"),
    (15, 11, "slime"),
    (25, 7, "slime"),
    (10, 16, "skeleton"),
    (20, 18, "skeleton"),
    (26, 3, "skeleton"),
    (32, 5, "slime"),
    (35, 12, "skeleton"),
    (30, 20, "slime"),
]

ENEMY_STATS = {
    "slime": {"hp": 30, "attack": 5, "defense": 2, "exp": 15, "gold": 5, "color": GREEN},
    "skeleton": {"hp": 50, "attack": 12, "defense": 5, "exp": 30, "gold": 15, "color": LIGHT_GRAY},
}

# Предметы
ITEMS = {
    "health_potion": {"name": "Зелье здоровья", "type": "consumable", "heal": 30, "price": 10, "color": RED},
    "mana_potion": {"name": "Зелье маны", "type": "consumable", "mana": 20, "price": 15, "color": BLUE},
    "iron_sword": {"name": "Железный меч", "type": "weapon", "attack": 8, "price": 50, "color": LIGHT_GRAY},
    "steel_sword": {"name": "Стальной меч", "type": "weapon", "attack": 15, "price": 100, "color": WHITE},
    "leather_armor": {"name": "Кожаная броня", "type": "armor", "defense": 5, "price": 40, "color": BROWN},
    "iron_armor": {"name": "Железная броня", "type": "armor", "defense": 12, "price": 80, "color": LIGHT_GRAY},
    "ore": {"name": "Руда", "type": "quest_item", "price": 0, "color": ORANGE},
}

ITEM_SPAWNS = [
    (2, 7, "health_potion"),
    (17, 6, "health_potion"),
    (26, 18, "iron_sword"),
    (14, 12, "ore"),
    (7, 17, "ore"),
    (24, 2, "leather_armor"),
    (10, 9, "mana_potion"),
    (32, 8, "health_potion"),
    (36, 15, "mana_potion"),
]


class GameSettings:
    """Класс для управления настройками игры"""

    def __init__(self):
        # Используем разрешение монитора по умолчанию
        self.native_width = NATIVE_WIDTH
        self.native_height = NATIVE_HEIGHT

        self.fullscreen = False
        self.music_volume = 70
        self.sfx_volume = 80
        self.show_fps = False
        self.show_minimap = True

        # Текущее разрешение (для оконного режима)
        self.screen_width = 1024
        self.screen_height = 768

        # Доступные разрешения (фильтруем по размеру монитора)
        all_resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
            (2560, 1440),
        ]

        # Оставляем только те разрешения, которые меньше или равны размеру монитора
        self.resolutions = [
            res for res in all_resolutions
            if res[0] <= self.native_width and res[1] <= self.native_height
        ]

        # Добавляем нативное разрешение, если его нет
        native_res = (self.native_width, self.native_height)
        if native_res not in self.resolutions:
            self.resolutions.append(native_res)
            self.resolutions.sort()

        self.current_resolution_index = 1 if len(self.resolutions) > 1 else 0

        # Загружаем сохранённые настройки
        self.load()

    def get_current_resolution(self):
        """Получить текущее разрешение с учётом режима"""
        if self.fullscreen:
            return (self.native_width, self.native_height)
        else:
            return self.resolutions[self.current_resolution_index]

    def save(self):
        """Сохранение настроек в файл"""
        data = {
            "fullscreen": self.fullscreen,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "show_fps": self.show_fps,
            "show_minimap": self.show_minimap,
            "resolution_index": self.current_resolution_index,
        }

        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ Настройки сохранены")
        except Exception as e:
            print(f"❌ Ошибка сохранения настроек: {e}")

    def load(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.fullscreen = data.get("fullscreen", False)
                self.music_volume = data.get("music_volume", 70)
                self.sfx_volume = data.get("sfx_volume", 80)
                self.show_fps = data.get("show_fps", False)
                self.show_minimap = data.get("show_minimap", True)

                res_index = data.get("resolution_index", 1)
                if 0 <= res_index < len(self.resolutions):
                    self.current_resolution_index = res_index

                w, h = self.resolutions[self.current_resolution_index]
                self.screen_width = w
                self.screen_height = h

                print("✅ Настройки загружены")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить настройки: {e}")

    def get_resolution(self):
        """Получить текущее разрешение для оконного режима"""
        return self.resolutions[self.current_resolution_index]

    def next_resolution(self):
        """Переключить на следующее разрешение"""
        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
        self.screen_width, self.screen_height = self.resolutions[self.current_resolution_index]

    def prev_resolution(self):
        """Переключить на предыдущее разрешение"""
        self.current_resolution_index = (self.current_resolution_index - 1) % len(self.resolutions)
        self.screen_width, self.screen_height = self.resolutions[self.current_resolution_index]


# Глобальный объект настроек
GAME_SETTINGS = GameSettings()