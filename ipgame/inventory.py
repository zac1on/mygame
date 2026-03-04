# inventory.py
import pygame
import os
from settings import *


class Inventory:
    def __init__(self):
        self.items = {}
        self.max_slots = 20

    def add_item(self, item_key, count=1):
        if item_key in self.items:
            self.items[item_key] += count
        elif len(self.items) < self.max_slots:
            self.items[item_key] = count
            return True
        else:
            return False
        return True

    def remove_item(self, item_key, count=1):
        if item_key in self.items:
            self.items[item_key] -= count
            if self.items[item_key] <= 0:
                del self.items[item_key]
            return True
        return False

    def has_item(self, item_key, count=1):
        return self.items.get(item_key, 0) >= count

    def count_item(self, item_key):
        return self.items.get(item_key, 0)

    def get_items_list(self):
        return list(self.items.items())


class InventoryUI:
    def __init__(self):
        self.visible = False
        self.selected_index = 0
        self.slot_size = 64
        self.cols = 5
        self.padding = 10
        self.offset_x = 0
        self.offset_y = 0

        # Загрузка спрайтов предметов
        self.item_sprites = {}
        self._load_item_sprites()

    def _load_item_sprites(self):
        """Загрузка спрайтов предметов для инвентаря"""
        sprite_size = 48

        for item_key in ITEMS.keys():
            paths = [
                f"assets/items/{item_key}.png",
                f"assets/{item_key}.png",
            ]

            for path in paths:
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        self.item_sprites[item_key] = pygame.transform.scale(
                            sprite, (sprite_size, sprite_size))
                        break
                    except Exception as e:
                        print(f"Ошибка загрузки спрайта {path}: {e}")

    def toggle(self):
        self.visible = not self.visible
        self.selected_index = 0

    def _calculate_position(self):
        rows = 4
        width = self.cols * (self.slot_size + self.padding) + self.padding
        height = rows * (self.slot_size + self.padding) + self.padding + 120
        self.offset_x = (SCREEN_WIDTH - width) // 2
        self.offset_y = (SCREEN_HEIGHT - height) // 2
        return width, height

    def handle_input(self, event, inventory, player):
        if not self.visible:
            return None

        items = inventory.get_items_list()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - self.cols)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(items) - 1, self.selected_index + self.cols)
            elif event.key == pygame.K_LEFT:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = min(len(items) - 1, self.selected_index + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 0 <= self.selected_index < len(items):
                    item_key, count = items[self.selected_index]
                    return self._use_item(item_key, inventory, player)

        return None

    def _use_item(self, item_key, inventory, player):
        item = ITEMS.get(item_key)
        if not item:
            return None

        if item["type"] == "consumable":
            if "heal" in item:
                player.heal(item["heal"])
                inventory.remove_item(item_key)
                return f"Восстановлено {item['heal']} HP"
            elif "mana" in item:
                player.restore_mana(item["mana"])
                inventory.remove_item(item_key)
                return f"Восстановлено {item['mana']} маны"

        elif item["type"] == "weapon":
            player.weapon = item_key
            return f"Экипировано: {item['name']}"

        elif item["type"] == "armor":
            player.armor = item_key
            return f"Экипировано: {item['name']}"

        return None

    def draw(self, surface, inventory, player):
        if not self.visible:
            return

        width, height = self._calculate_position()
        items = inventory.get_items_list()

        # Фон инвентаря
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((20, 20, 40, 230))
        surface.blit(bg, (self.offset_x, self.offset_y))
        pygame.draw.rect(surface, GOLD,
                         (self.offset_x, self.offset_y, width, height), 2,
                         border_radius=8)

        # Заголовок
        font = pygame.font.SysFont("Arial", 22, bold=True)
        title = font.render("📦 Инвентарь", True, GOLD)
        surface.blit(title, (self.offset_x + 15, self.offset_y + 10))

        # Слоты
        small_font = pygame.font.SysFont("Arial", 14)
        for i in range(min(20, max(len(items), self.cols * 4))):
            col = i % self.cols
            row = i // self.cols
            x = self.offset_x + self.padding + col * (self.slot_size + self.padding)
            y = self.offset_y + 45 + row * (self.slot_size + self.padding)

            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)

            # Выбранный слот
            if i == self.selected_index:
                pygame.draw.rect(surface, GOLD, slot_rect, border_radius=4)
                inner = slot_rect.inflate(-4, -4)
                pygame.draw.rect(surface, DARK_GRAY, inner, border_radius=3)
            else:
                pygame.draw.rect(surface, (50, 50, 70), slot_rect, border_radius=4)
                pygame.draw.rect(surface, (80, 80, 100), slot_rect, 1, border_radius=4)

            if i < len(items):
                item_key, count = items[i]
                item = ITEMS[item_key]

                # Спрайт или стандартная отрисовка
                if item_key in self.item_sprites:
                    sprite = self.item_sprites[item_key]
                    sprite_rect = sprite.get_rect(center=slot_rect.center)
                    surface.blit(sprite, sprite_rect)
                else:
                    self._draw_item_icon(surface, slot_rect, item_key, item)

                # Количество
                if count > 1:
                    count_surf = small_font.render(str(count), True, WHITE)
                    # Фон для числа
                    count_bg = pygame.Surface((count_surf.get_width() + 4, count_surf.get_height()), pygame.SRCALPHA)
                    count_bg.fill((0, 0, 0, 180))
                    surface.blit(count_bg, (x + self.slot_size - count_surf.get_width() - 6, y + self.slot_size - 18))
                    surface.blit(count_surf, (x + self.slot_size - count_surf.get_width() - 4, y + self.slot_size - 18))

                # Индикатор экипировки
                if player.weapon == item_key or player.armor == item_key:
                    equip_surf = small_font.render("E", True, GREEN)
                    pygame.draw.circle(surface, (0, 100, 0), (x + 12, y + 12), 10)
                    surface.blit(equip_surf, (x + 8, y + 5))

        # Описание выбранного предмета
        self._draw_item_description(surface, items, player, width, height)

    def _draw_item_icon(self, surface, slot_rect, item_key, item):
        """Красивая отрисовка иконки предмета в инвентаре"""
        cx, cy = slot_rect.centerx, slot_rect.centery
        color = item["color"]

        if "potion" in item_key:
            self._draw_potion_icon(surface, cx, cy, color)
        elif "sword" in item_key:
            self._draw_sword_icon(surface, cx, cy, color)
        elif "armor" in item_key:
            self._draw_armor_icon(surface, cx, cy, color)
        elif item_key == "ore":
            self._draw_ore_icon(surface, cx, cy, color)
        else:
            # Универсальная иконка
            icon_rect = pygame.Rect(cx - 20, cy - 20, 40, 40)
            pygame.draw.rect(surface, color, icon_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, icon_rect, 2, border_radius=8)
            font = pygame.font.SysFont("Arial", 20, bold=True)
            letter = item["name"][0]
            letter_surf = font.render(letter, True, WHITE)
            surface.blit(letter_surf, letter_surf.get_rect(center=(cx, cy)))

    def _draw_potion_icon(self, surface, cx, cy, color):
        """Иконка зелья"""
        # Бутылка
        bottle_rect = pygame.Rect(cx - 12, cy - 8, 24, 28)
        pygame.draw.rect(surface, color, bottle_rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, bottle_rect, 2, border_radius=6)

        # Горлышко
        pygame.draw.rect(surface, (180, 180, 180), (cx - 6, cy - 16, 12, 8))
        pygame.draw.rect(surface, (150, 150, 150), (cx - 6, cy - 16, 12, 8), 1)

        # Пробка
        pygame.draw.rect(surface, (139, 90, 43), (cx - 5, cy - 22, 10, 6), border_radius=2)

        # Блик
        pygame.draw.line(surface, WHITE, (cx - 6, cy - 4), (cx - 6, cy + 10), 3)

        # Пузырьки
        pygame.draw.circle(surface, WHITE, (cx + 4, cy + 6), 3)
        pygame.draw.circle(surface, WHITE, (cx - 2, cy + 2), 2)

    def _draw_sword_icon(self, surface, cx, cy, color):
        """Иконка меча"""
        # Клинок
        pygame.draw.polygon(surface, color, [
            (cx + 12, cy - 18),  # Остриё
            (cx + 16, cy - 12),
            (cx - 4, cy + 10),
            (cx - 8, cy + 6),
        ])
        pygame.draw.polygon(surface, WHITE, [
            (cx + 12, cy - 18),
            (cx + 16, cy - 12),
            (cx - 4, cy + 10),
            (cx - 8, cy + 6),
        ], 2)

        # Блик на клинке
        pygame.draw.line(surface, WHITE, (cx + 8, cy - 12), (cx - 2, cy + 4), 2)

        # Гарда
        pygame.draw.rect(surface, GOLD, (cx - 14, cy + 6, 20, 6), border_radius=2)
        pygame.draw.rect(surface, (180, 140, 0), (cx - 14, cy + 6, 20, 6), 1, border_radius=2)

        # Рукоять
        pygame.draw.rect(surface, (100, 60, 20), (cx - 8, cy + 10, 8, 14), border_radius=2)
        pygame.draw.rect(surface, (80, 40, 10), (cx - 8, cy + 10, 8, 14), 1, border_radius=2)

        # Навершие
        pygame.draw.circle(surface, GOLD, (cx - 4, cy + 24), 5)

    def _draw_armor_icon(self, surface, cx, cy, color):
        """Иконка брони"""
        # Основа брони
        armor_points = [
            (cx, cy - 20),       # Верх
            (cx + 18, cy - 12),  # Правое плечо
            (cx + 16, cy + 16),  # Правый низ
            (cx, cy + 20),       # Низ центр
            (cx - 16, cy + 16),  # Левый низ
            (cx - 18, cy - 12),  # Левое плечо
        ]
        pygame.draw.polygon(surface, color, armor_points)
        pygame.draw.polygon(surface, WHITE, armor_points, 2)

        # Вырез для шеи
        pygame.draw.arc(surface, (40, 40, 40), (cx - 8, cy - 22, 16, 10), 0, 3.14, 3)

        # Детали
        pygame.draw.line(surface, WHITE, (cx, cy - 10), (cx, cy + 10), 2)
        pygame.draw.line(surface, WHITE, (cx - 10, cy), (cx + 10, cy), 2)

    def _draw_ore_icon(self, surface, cx, cy, color):
        """Иконка руды"""
        # Камень
        stone_points = [
            (cx - 16, cy + 12),
            (cx - 12, cy - 8),
            (cx + 4, cy - 16),
            (cx + 16, cy - 6),
            (cx + 12, cy + 14),
            (cx - 6, cy + 14),
        ]
        pygame.draw.polygon(surface, (100, 100, 100), stone_points)
        pygame.draw.polygon(surface, (70, 70, 70), stone_points, 2)

        # Металлические жилы
        pygame.draw.line(surface, color, (cx - 8, cy), (cx + 6, cy - 6), 4)
        pygame.draw.line(surface, color, (cx - 2, cy + 6), (cx + 8, cy + 4), 3)

        # Блеск
        pygame.draw.circle(surface, WHITE, (cx + 4, cy - 2), 3)
        pygame.draw.circle(surface, (255, 200, 100), (cx - 4, cy + 4), 2)

    def _draw_item_description(self, surface, items, player, width, height):
        """Отрисовка описания выбранного предмета"""
        small_font = pygame.font.SysFont("Arial", 14)
        desc_y = self.offset_y + height - 65

        if 0 <= self.selected_index < len(items):
            item_key, count = items[self.selected_index]
            item = ITEMS[item_key]

            # Название
            name_color = GOLD if item["type"] == "weapon" or item["type"] == "armor" else WHITE
            name_surf = small_font.render(f"{item['name']} (x{count})", True, name_color)
            surface.blit(name_surf, (self.offset_x + 15, desc_y))

            # Характеристики
            info = ""
            if "heal" in item:
                info = f"❤️ Лечит: +{item['heal']} HP"
            elif "mana" in item:
                info = f"💙 Мана: +{item['mana']}"
            elif "attack" in item:
                equipped = " ✅ [Экипировано]" if player.weapon == item_key else ""
                info = f"⚔️ Атака: +{item['attack']}{equipped}"
            elif "defense" in item:
                equipped = " ✅ [Экипировано]" if player.armor == item_key else ""
                info = f"🛡️ Защита: +{item['defense']}{equipped}"
            elif item["type"] == "quest_item":
                info = "📜 Квестовый предмет"

            if info:
                info_surf = small_font.render(info, True, LIGHT_GRAY)
                surface.blit(info_surf, (self.offset_x + 15, desc_y + 20))

            # Подсказка
            if item["type"] in ["consumable", "weapon", "armor"]:
                hint_surf = small_font.render("[Enter] Использовать", True, YELLOW)
                surface.blit(hint_surf, (self.offset_x + width - 160, desc_y + 20))
        else:
            empty_surf = small_font.render("Инвентарь пуст", True, LIGHT_GRAY)
            surface.blit(empty_surf, (self.offset_x + 15, desc_y))