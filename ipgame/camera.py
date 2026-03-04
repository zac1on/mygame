# camera.py
import pygame
from settings import *


class Camera:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0
        self.y = 0
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

    def update_screen_size(self, screen_width, screen_height):
        """Обновить размер экрана для адаптации камеры"""
        self.screen_width = screen_width
        self.screen_height = screen_height

    def apply(self, rect):
        """Сдвигает прямоугольник относительно камеры"""
        return rect.move(self.x, self.y)

    def apply_pos(self, pos):
        """Сдвигает позицию (x, y) относительно камеры"""
        return (pos[0] + self.x, pos[1] + self.y)

    def update(self, target_rect):
        """Центрирует камеру на цели с учётом текущего размера экрана"""
        # Целевая позиция камеры (центрируем на игроке)
        x = -target_rect.centerx + self.screen_width // 2
        y = -target_rect.centery + self.screen_height // 2

        # Ограничения камеры (не выходить за пределы карты)
        # Левая граница
        x = min(0, x)
        # Верхняя граница
        y = min(0, y)
        # Правая граница
        x = max(-(self.map_width - self.screen_width), x)
        # Нижняя граница
        y = max(-(self.map_height - self.screen_height), y)

        # Если карта меньше экрана - центрируем карту
        if self.map_width < self.screen_width:
            x = (self.screen_width - self.map_width) // 2
        if self.map_height < self.screen_height:
            y = (self.screen_height - self.map_height) // 2

        self.x = x
        self.y = y