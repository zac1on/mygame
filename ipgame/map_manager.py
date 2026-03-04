# map_manager.py
import pygame
from settings import *


class MapManager:
    def __init__(self):
        self.map_data = GAME_MAP
        self.walls = []
        self.water = []
        self.map_width = len(self.map_data[0]) * TILE_SIZE
        self.map_height = len(self.map_data) * TILE_SIZE
        self._build_collision()

    def _build_collision(self):
        """Создаёт прямоугольники столкновений"""
        for row in range(len(self.map_data)):
            for col in range(len(self.map_data[row])):
                tile = self.map_data[row][col]
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)
                if tile == 1:
                    self.walls.append(rect)
                elif tile == 2:
                    self.water.append(rect)
                    self.walls.append(rect)
                elif tile == 4:
                    tree_col = pygame.Rect(col * TILE_SIZE + 10,
                                           row * TILE_SIZE + 30,
                                           TILE_SIZE - 20, TILE_SIZE - 30)
                    self.walls.append(tree_col)

    def draw(self, surface, camera):
        """Отрисовка карты с учётом размера экрана"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()

        # Вычисляем видимую область в тайлах
        # Добавляем запас в 2 тайла по краям для плавности
        start_col = max(0, int(-camera.x // TILE_SIZE) - 1)
        end_col = min(len(self.map_data[0]), int((-camera.x + screen_width) // TILE_SIZE) + 2)
        start_row = max(0, int(-camera.y // TILE_SIZE) - 1)
        end_row = min(len(self.map_data), int((-camera.y + screen_height) // TILE_SIZE) + 2)

        # Отрисовываем только видимые тайлы
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if row < 0 or row >= len(self.map_data):
                    continue
                if col < 0 or col >= len(self.map_data[row]):
                    continue

                tile = self.map_data[row][col]
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)
                draw_rect = camera.apply(rect)

                if tile == 0:
                    self._draw_grass(surface, draw_rect)
                elif tile == 1:
                    self._draw_wall(surface, draw_rect)
                elif tile == 2:
                    self._draw_water(surface, draw_rect)
                elif tile == 3:
                    self._draw_road(surface, draw_rect)
                elif tile == 4:
                    self._draw_grass(surface, draw_rect)
                    self._draw_tree(surface, draw_rect)

        # Заполняем фон за пределами карты
        self._draw_background_outside_map(surface, camera, screen_width, screen_height)

    def _draw_background_outside_map(self, surface, camera, screen_width, screen_height):
        """Заполнение фона за пределами карты"""
        bg_color = (20, 40, 20)  # Тёмно-зелёный

        # Левая область
        if camera.x > 0:
            pygame.draw.rect(surface, bg_color, (0, 0, camera.x, screen_height))

        # Правая область
        right_edge = camera.x + self.map_width
        if right_edge < screen_width:
            pygame.draw.rect(surface, bg_color, (right_edge, 0, screen_width - right_edge, screen_height))

        # Верхняя область
        if camera.y > 0:
            pygame.draw.rect(surface, bg_color, (0, 0, screen_width, camera.y))

        # Нижняя область
        bottom_edge = camera.y + self.map_height
        if bottom_edge < screen_height:
            pygame.draw.rect(surface, bg_color, (0, bottom_edge, screen_width, screen_height - bottom_edge))

    def _draw_grass(self, surface, rect):
        pygame.draw.rect(surface, (70, 140, 50), rect)
        for i in range(3):
            gx = rect.x + 10 + i * 18
            gy = rect.y + 20 + (i * 13) % 30
            pygame.draw.line(surface, (90, 170, 60),
                             (gx, gy), (gx + 3, gy - 8), 2)

    def _draw_wall(self, surface, rect):
        pygame.draw.rect(surface, (100, 90, 80), rect)
        pygame.draw.rect(surface, (80, 70, 60), rect, 2)
        for i in range(2):
            y = rect.y + 10 + i * 25
            pygame.draw.line(surface, (70, 60, 50),
                             (rect.x, y), (rect.right, y), 1)
            if i % 2 == 0:
                pygame.draw.line(surface, (70, 60, 50),
                                 (rect.centerx, y),
                                 (rect.centerx, y + 25), 1)

    def _draw_water(self, surface, rect):
        pygame.draw.rect(surface, (40, 100, 200), rect)
        import math
        t = pygame.time.get_ticks() / 1000
        for i in range(3):
            y = rect.y + 15 + i * 18
            points = []
            for x in range(rect.x, rect.right, 4):
                wy = y + math.sin(x * 0.1 + t * 2 + i) * 3
                points.append((x, wy))
            if len(points) > 1:
                pygame.draw.lines(surface, (80, 150, 255), False, points, 1)

    def _draw_road(self, surface, rect):
        pygame.draw.rect(surface, (160, 140, 100), rect)
        pygame.draw.rect(surface, (140, 120, 80), rect, 1)
        for i in range(2):
            dx = rect.x + 15 + i * 30
            dy = rect.y + 10 + (i * 20) % 40
            pygame.draw.circle(surface, (130, 110, 70), (dx, dy), 3)

    def _draw_tree(self, surface, rect):
        cx = rect.centerx
        trunk = pygame.Rect(cx - 6, rect.centery + 5, 12, 30)
        pygame.draw.rect(surface, (100, 70, 40), trunk)

        pygame.draw.circle(surface, (30, 120, 30), (cx, rect.centery - 5), 20)
        pygame.draw.circle(surface, (40, 140, 40), (cx - 10, rect.centery), 15)
        pygame.draw.circle(surface, (40, 140, 40), (cx + 10, rect.centery), 15)
        pygame.draw.circle(surface, (50, 160, 50), (cx, rect.centery - 12), 14)