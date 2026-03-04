# button.py
import pygame
from settings import *


class Button:
    """Универсальная кнопка с поддержкой мыши и клавиатуры"""

    def __init__(self, x, y, width, height, text,
                 color=BLUE, hover_color=None, text_color=WHITE,
                 border_color=WHITE, border_width=3,
                 font_size=20, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or self._lighten_color(color, 40)
        self.text_color = text_color
        self.border_color = border_color
        self.border_width = border_width
        self.font_size = font_size
        self.icon = icon

        self.is_hovered = False
        self.is_selected = False
        self.is_pressed = False

        self.hover_offset = 0

    def _lighten_color(self, color, amount):
        return (min(255, color[0] + amount), min(255, color[1] + amount), min(255, color[2] + amount))

    def _darken_color(self, color, amount):
        return (max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount))

    def set_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def update(self, mouse_pos):
        """Обновление состояния кнопки"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target_offset = 2 if self.is_hovered or self.is_selected else 0
        self.hover_offset += (target_offset - self.hover_offset) * 0.3

    def check_click(self, mouse_pos):
        """Проверка клика по кнопке"""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Отрисовка кнопки в стиле Pokemon"""
        x = self.rect.x
        y = self.rect.y - int(self.hover_offset)
        w = self.rect.width
        h = self.rect.height

        if self.is_pressed:
            bg_color = self._darken_color(self.color, 30)
            y += 2
        elif self.is_hovered or self.is_selected:
            bg_color = self.hover_color
        else:
            bg_color = self.color

        # Тень
        shadow_rect = pygame.Rect(x + 3, y + 4, w, h)
        pygame.draw.rect(surface, (20, 20, 20), shadow_rect, border_radius=8)

        # Основа
        main_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, bg_color, main_rect, border_radius=8)

        # Блик
        highlight_rect = pygame.Rect(x + 2, y + 2, w - 4, h // 3)
        highlight_color = self._lighten_color(bg_color, 30)
        pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=6)

        # Граница
        border_color = GOLD if (self.is_hovered or self.is_selected) else self.border_color
        pygame.draw.rect(surface, border_color, main_rect, self.border_width, border_radius=8)

        # Текст
        font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))

        # Тень текста
        shadow_surf = font.render(self.text, True, (30, 30, 30))
        surface.blit(shadow_surf, text_rect.move(2, 2))
        surface.blit(text_surf, text_rect)


class ButtonGroup:
    """Группа кнопок с навигацией"""

    def __init__(self):
        self.buttons = []
        self.selected_index = 0

    def add_button(self, button):
        self.buttons.append(button)

    def clear(self):
        self.buttons = []
        self.selected_index = 0

    def update(self, mouse_pos):
        """Обновление всех кнопок"""
        for i, button in enumerate(self.buttons):
            button.update(mouse_pos)
            button.is_selected = (i == self.selected_index)

            if button.is_hovered:
                self.selected_index = i

    def handle_click(self, mouse_pos):
        """Обработка клика мыши - возвращает индекс нажатой кнопки или None"""
        for i, button in enumerate(self.buttons):
            if button.check_click(mouse_pos):
                self.selected_index = i
                return i
        return None

    def handle_keyboard(self, key):
        """Обработка клавиатуры - возвращает индекс при Enter или None"""
        if key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % max(1, len(self.buttons))
            return None
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % max(1, len(self.buttons))
            return None
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.selected_index
        return None

    def draw(self, surface):
        for button in self.buttons:
            button.draw(surface)


class Panel:
    """Панель в стиле Pokemon"""

    def __init__(self, x, y, width, height, bg_color=(40, 45, 60), border_color=WHITE, border_width=4):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

    def draw(self, surface, title=None):
        x, y, w, h = self.rect

        # Тень
        shadow = pygame.Rect(x + 4, y + 4, w, h)
        pygame.draw.rect(surface, (15, 15, 25), shadow, border_radius=12)

        # Фон
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=12)

        # Блик
        inner = pygame.Rect(x + 4, y + 4, w - 8, h // 3)
        lighter = (min(255, self.bg_color[0] + 15), min(255, self.bg_color[1] + 15), min(255, self.bg_color[2] + 20))
        pygame.draw.rect(surface, lighter, inner, border_radius=10)

        # Границы
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, border_radius=12)
        inner_border = self.rect.inflate(-8, -8)
        darker = (
        max(0, self.border_color[0] - 100), max(0, self.border_color[1] - 100), max(0, self.border_color[2] - 100))
        pygame.draw.rect(surface, darker, inner_border, 2, border_radius=10)

        if title:
            font = pygame.font.SysFont("Arial", 24, bold=True)
            title_surf = font.render(title, True, WHITE)
            title_rect = title_surf.get_rect(centerx=x + w // 2, y=y + 15)

            title_bg = title_rect.inflate(20, 8)
            pygame.draw.rect(surface, (30, 35, 50), title_bg, border_radius=6)
            pygame.draw.rect(surface, GOLD, title_bg, 2, border_radius=6)
            surface.blit(title_surf, title_rect)


class HealthBar:
    """Полоска здоровья"""

    def __init__(self, x, y, width, height, max_value, current_value=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = current_value if current_value is not None else max_value

    def set_value(self, value):
        self.current_value = max(0, min(value, self.max_value))

    def draw(self, surface, label="HP", show_numbers=True, bar_color=None):
        x, y, w, h = self.rect

        # Фон
        pygame.draw.rect(surface, (40, 40, 40), self.rect, border_radius=4)

        # Заполнение
        ratio = self.current_value / self.max_value if self.max_value > 0 else 0
        fill_width = int((w - 4) * ratio)

        if fill_width > 0:
            if bar_color:
                color = bar_color
            elif ratio > 0.5:
                color = (50, 205, 50)
            elif ratio > 0.25:
                color = (255, 200, 0)
            else:
                color = (220, 50, 50)

            fill_rect = pygame.Rect(x + 2, y + 2, fill_width, h - 4)
            pygame.draw.rect(surface, color, fill_rect, border_radius=3)

            # Блик
            highlight = pygame.Rect(x + 2, y + 2, fill_width, (h - 4) // 3)
            lighter = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            pygame.draw.rect(surface, lighter, highlight, border_radius=3)

        # Граница
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=4)

        # Метка
        font = pygame.font.SysFont("Arial", 12, bold=True)
        label_surf = font.render(label, True, WHITE)
        surface.blit(label_surf, (x - label_surf.get_width() - 5, y + (h - label_surf.get_height()) // 2))

        # Числа
        if show_numbers:
            numbers = f"{int(self.current_value)}/{self.max_value}"
            num_surf = font.render(numbers, True, WHITE)
            surface.blit(num_surf, (x + w + 5, y + (h - num_surf.get_height()) // 2))