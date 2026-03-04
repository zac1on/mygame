# npc.py
import pygame
import os
from settings import *


class NPC:
    def __init__(self, x, y, name, dialogues, quest_id=None):
        # Увеличенный размер
        self.size = TILE_SIZE + 8
        self.rect = pygame.Rect(x * TILE_SIZE - 4, y * TILE_SIZE - 4,
                                self.size, self.size)

        self.name = name
        self.dialogues = dialogues
        self.quest_id = quest_id
        self.interaction_range = 90

        # Загрузка спрайта
        self.sprite = None
        self._load_sprite()

    def _load_sprite(self):
        """Загрузка спрайта NPC по имени"""

        # Определяем файл спрайта по имени NPC
        sprite_map = {
            "Кузнец": ["assets/npc_blacksmith.png", "assets/blacksmith.png"],
            "Торговец": ["assets/npc_merchant.png", "assets/merchant.png"],
            "Старейшина": ["assets/npc_elder.png", "assets/elder.png"],
        }

        # Получаем пути для этого NPC
        paths = sprite_map.get(self.name, [f"assets/npc_{self.name.lower()}.png"])

        # Пробуем загрузить
        for path in paths:
            if os.path.exists(path):
                try:
                    self.sprite = pygame.image.load(path).convert_alpha()
                    self.sprite = pygame.transform.scale(self.sprite, (self.size, self.size))
                    print(f"✅ Загружен спрайт NPC: {path} -> {self.name}")
                    return
                except Exception as e:
                    print(f"❌ Ошибка загрузки {path}: {e}")

        print(f"⚠️ Спрайт для NPC '{self.name}' не найден, используется стандартная отрисовка")

    def can_interact(self, player_rect):
        dist = ((self.rect.centerx - player_rect.centerx) ** 2 +
                (self.rect.centery - player_rect.centery) ** 2) ** 0.5
        return dist < self.interaction_range

    def draw(self, surface, camera, player_rect):
        draw_rect = camera.apply(self.rect)

        # Тень под NPC
        shadow_surf = pygame.Surface((self.size - 10, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect())
        shadow_pos = (draw_rect.centerx - (self.size - 10) // 2, draw_rect.bottom - 4)
        surface.blit(shadow_surf, shadow_pos)

        # Спрайт или стандартная отрисовка
        if self.sprite:
            surface.blit(self.sprite, draw_rect)
        else:
            self._draw_default(surface, draw_rect)

        # Имя над головой
        self._draw_name(surface, draw_rect)

        # Индикатор взаимодействия
        if self.can_interact(player_rect):
            self._draw_interaction_hint(surface, draw_rect)

    def _draw_default(self, surface, draw_rect):
        """Стандартная отрисовка NPC по типу"""

        if self.name == "Кузнец":
            self._draw_blacksmith(surface, draw_rect)
        elif self.name == "Торговец":
            self._draw_merchant(surface, draw_rect)
        else:
            self._draw_generic(surface, draw_rect)

    def _draw_blacksmith(self, surface, draw_rect):
        """Отрисовка кузнеца"""
        # Тело (коричневый фартук)
        body_color = (139, 90, 43)  # Коричневый
        pygame.draw.rect(surface, body_color, draw_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 60, 30), draw_rect, 2, border_radius=8)

        # Голова (лысая, загорелая)
        head_rect = pygame.Rect(draw_rect.centerx - 14, draw_rect.top + 4, 28, 28)
        pygame.draw.ellipse(surface, (210, 150, 100), head_rect)  # Загорелая кожа
        pygame.draw.ellipse(surface, (180, 120, 80), head_rect, 2)

        # Борода
        beard_rect = pygame.Rect(draw_rect.centerx - 10, draw_rect.top + 22, 20, 12)
        pygame.draw.ellipse(surface, (60, 40, 20), beard_rect)  # Тёмная борода

        # Глаза (серьёзные)
        pygame.draw.circle(surface, WHITE, (draw_rect.centerx - 6, draw_rect.top + 14), 4)
        pygame.draw.circle(surface, WHITE, (draw_rect.centerx + 6, draw_rect.top + 14), 4)
        pygame.draw.circle(surface, BLACK, (draw_rect.centerx - 6, draw_rect.top + 15), 2)
        pygame.draw.circle(surface, BLACK, (draw_rect.centerx + 6, draw_rect.top + 15), 2)

        # Брови (нахмуренные)
        pygame.draw.line(surface, (60, 40, 20),
                         (draw_rect.centerx - 10, draw_rect.top + 10),
                         (draw_rect.centerx - 3, draw_rect.top + 12), 2)
        pygame.draw.line(surface, (60, 40, 20),
                         (draw_rect.centerx + 10, draw_rect.top + 10),
                         (draw_rect.centerx + 3, draw_rect.top + 12), 2)

    def _draw_merchant(self, surface, draw_rect):
        """Отрисовка торговца"""
        # Тело (фиолетовая роба)
        body_color = (128, 0, 128)  # Фиолетовый
        pygame.draw.rect(surface, body_color, draw_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 0, 100), draw_rect, 2, border_radius=10)

        # Золотая отделка
        pygame.draw.line(surface, GOLD,
                         (draw_rect.centerx, draw_rect.top + 30),
                         (draw_rect.centerx, draw_rect.bottom - 5), 3)

        # Голова (круглая, розовые щёки)
        head_rect = pygame.Rect(draw_rect.centerx - 14, draw_rect.top + 2, 28, 28)
        pygame.draw.ellipse(surface, (255, 218, 185), head_rect)  # Светлая кожа

        # Розовые щёки
        pygame.draw.circle(surface, (255, 182, 193), (draw_rect.centerx - 10, draw_rect.top + 20), 4)
        pygame.draw.circle(surface, (255, 182, 193), (draw_rect.centerx + 10, draw_rect.top + 20), 4)

        # Глаза (добрые, прищуренные от улыбки)
        pygame.draw.arc(surface, BLACK,
                        (draw_rect.centerx - 10, draw_rect.top + 10, 8, 8),
                        0, 3.14, 2)
        pygame.draw.arc(surface, BLACK,
                        (draw_rect.centerx + 2, draw_rect.top + 10, 8, 8),
                        0, 3.14, 2)

        # Усы
        pygame.draw.arc(surface, (100, 70, 40),
                        (draw_rect.centerx - 8, draw_rect.top + 18, 7, 6),
                        3.14, 6.28, 2)
        pygame.draw.arc(surface, (100, 70, 40),
                        (draw_rect.centerx + 1, draw_rect.top + 18, 7, 6),
                        3.14, 6.28, 2)

        # Большая улыбка
        pygame.draw.arc(surface, BLACK,
                        (draw_rect.centerx - 8, draw_rect.top + 20, 16, 10),
                        3.14, 6.28, 2)

        # Шапка/колпак
        hat_points = [
            (draw_rect.centerx - 16, draw_rect.top + 6),
            (draw_rect.centerx, draw_rect.top - 8),
            (draw_rect.centerx + 16, draw_rect.top + 6),
        ]
        pygame.draw.polygon(surface, (180, 0, 0), hat_points)
        pygame.draw.polygon(surface, GOLD, hat_points, 2)

    def _draw_generic(self, surface, draw_rect):
        """Стандартная отрисовка NPC (Старейшина и др.)"""
        # Тело (зелёная одежда)
        pygame.draw.rect(surface, (80, 160, 80), draw_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 120, 60), draw_rect, 2, border_radius=10)

        # Голова
        head_rect = pygame.Rect(draw_rect.centerx - 16, draw_rect.top + 6, 32, 32)
        pygame.draw.ellipse(surface, (240, 200, 160), head_rect)
        pygame.draw.ellipse(surface, (200, 160, 120), head_rect, 2)

        # Глаза
        pygame.draw.circle(surface, BLACK, (draw_rect.centerx - 7, draw_rect.top + 18), 4)
        pygame.draw.circle(surface, BLACK, (draw_rect.centerx + 7, draw_rect.top + 18), 4)

        # Улыбка
        pygame.draw.arc(surface, BLACK,
                        (draw_rect.centerx - 8, draw_rect.top + 16, 16, 14),
                        3.14, 6.28, 2)

    def _draw_name(self, surface, draw_rect):
        """Отрисовка имени над NPC"""
        font = pygame.font.SysFont("Arial", 16, bold=True)
        name_surf = font.render(self.name, True, YELLOW)
        name_rect = name_surf.get_rect(centerx=draw_rect.centerx,
                                       bottom=draw_rect.top - 8)

        # Фон для имени
        bg_rect = name_rect.inflate(10, 4)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        surface.blit(bg_surface, bg_rect.topleft)
        pygame.draw.rect(surface, GOLD, bg_rect, 1, border_radius=4)
        surface.blit(name_surf, name_rect)

    def _draw_interaction_hint(self, surface, draw_rect):
        """Отрисовка подсказки взаимодействия"""
        font = pygame.font.SysFont("Arial", 14, bold=True)
        hint_surf = font.render("[E] Говорить", True, WHITE)
        hint_rect = hint_surf.get_rect(centerx=draw_rect.centerx,
                                       bottom=draw_rect.top - 28)

        bg_rect = hint_rect.inflate(12, 6)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        surface.blit(bg_surface, bg_rect.topleft)
        pygame.draw.rect(surface, GREEN, bg_rect, 2, border_radius=5)
        surface.blit(hint_surf, hint_rect)