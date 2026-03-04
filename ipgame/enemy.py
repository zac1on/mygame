# enemy.py
import pygame
import random
import math
import os
from settings import *


class Enemy:
    def __init__(self, x, y, enemy_type):
        self.type = enemy_type
        stats = ENEMY_STATS[enemy_type]

        # Увеличенный размер
        self.size = TILE_SIZE + 8
        self.rect = pygame.Rect(x * TILE_SIZE - 4, y * TILE_SIZE - 4,
                                self.size, self.size)

        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.attack = stats["attack"]
        self.defense = stats["defense"]
        self.exp_reward = stats["exp"]
        self.gold_reward = stats["gold"]
        self.color = stats["color"]

        self.alive = True
        self.aggro_range = 200
        self.speed = 2

        self.home_x = self.rect.x
        self.home_y = self.rect.y
        self.patrol_timer = 0
        self.patrol_dx = 0
        self.patrol_dy = 0

        self.anim_timer = 0
        self.hurt_timer = 0

        self.respawn_timer = 0
        self.respawn_time = 600

        # Загрузка спрайта
        self.sprite = None
        self._load_sprite()

        # Анимация движения
        self.bounce_offset = 0
        self.bounce_direction = 1

    def _load_sprite(self):
        """Загрузка спрайта врага"""
        sprite_paths = {
            "slime": ["assets/enemy_slime.png", "assets/slime.png"],
            "skeleton": ["assets/enemy_skeleton.png", "assets/skeleton.png"],
        }

        paths = sprite_paths.get(self.type, [f"assets/{self.type}.png"])

        for path in paths:
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    self.sprite = pygame.transform.scale(sprite, (self.size, self.size))
                    print(f"✅ Загружен спрайт врага: {path} -> {self.type}")
                    return
                except Exception as e:
                    print(f"❌ Ошибка загрузки {path}: {e}")

    def update(self, player_rect, walls):
        if not self.alive:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.alive = True
                self.hp = self.max_hp
                self.rect.x = self.home_x
                self.rect.y = self.home_y
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= 1

        # Анимация подпрыгивания (для слизней)
        if self.type == "slime":
            self.bounce_offset += 0.3 * self.bounce_direction
            if abs(self.bounce_offset) > 3:
                self.bounce_direction *= -1

        dist = math.hypot(player_rect.centerx - self.rect.centerx,
                          player_rect.centery - self.rect.centery)

        if dist < self.aggro_range:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            length = max(math.hypot(dx, dy), 1)
            dx = dx / length * self.speed
            dy = dy / length * self.speed

            collision_rect = self.rect.inflate(-16, -16)

            new_rect = collision_rect.move(int(dx), 0)
            if not self._collides(new_rect, walls):
                self.rect.x += int(dx)

            new_rect = collision_rect.move(0, int(dy))
            if not self._collides(new_rect, walls):
                self.rect.y += int(dy)
        else:
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_timer = random.randint(60, 180)
                self.patrol_dx = random.choice([-1, 0, 1])
                self.patrol_dy = random.choice([-1, 0, 1])

            collision_rect = self.rect.inflate(-16, -16)
            new_rect = collision_rect.move(self.patrol_dx, self.patrol_dy)
            if not self._collides(new_rect, walls):
                if abs(self.rect.x + self.patrol_dx - self.home_x) < 100 and \
                   abs(self.rect.y + self.patrol_dy - self.home_y) < 100:
                    self.rect.x += self.patrol_dx
                    self.rect.y += self.patrol_dy

    def _collides(self, rect, walls):
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False

    def take_damage(self, damage):
        actual = max(damage - self.defense, 1)
        self.hp -= actual
        self.hurt_timer = 10
        if self.hp <= 0:
            self.alive = False
            self.respawn_timer = self.respawn_time
        return actual

    def draw(self, surface, camera):
        if not self.alive:
            return

        draw_rect = camera.apply(self.rect)

        # Эффект мигания при уроне
        if self.hurt_timer > 0 and self.hurt_timer % 4 < 2:
            # Пропускаем кадр для эффекта мигания
            return

        # Тень под врагом
        shadow_surf = pygame.Surface((self.size - 15, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect())
        shadow_pos = (draw_rect.centerx - (self.size - 15) // 2, draw_rect.bottom - 6)
        surface.blit(shadow_surf, shadow_pos)

        # Смещение для анимации (подпрыгивание)
        anim_offset = int(self.bounce_offset) if self.type == "slime" else 0

        # Спрайт или стандартная отрисовка
        if self.sprite:
            sprite_rect = draw_rect.move(0, -anim_offset)
            surface.blit(self.sprite, sprite_rect)
        else:
            # Красивая стандартная отрисовка
            if self.type == "slime":
                self._draw_slime(surface, draw_rect, anim_offset)
            elif self.type == "skeleton":
                self._draw_skeleton(surface, draw_rect)
            else:
                self._draw_generic(surface, draw_rect)

        # Полоска здоровья
        if self.hp < self.max_hp:
            self._draw_health_bar(surface, draw_rect)

    def _draw_slime(self, surface, rect, anim_offset):
        """Красивая отрисовка слизня на карте"""
        cx = rect.centerx
        cy = rect.centery - anim_offset

        # Размер слизня
        radius = self.size // 2 - 5

        # Тело (основной цвет)
        pygame.draw.circle(surface, self.color, (cx, cy + 8), radius)

        # Обводка (темнее)
        dark_color = (max(self.color[0] - 50, 0),
                      max(self.color[1] - 50, 0),
                      max(self.color[2] - 50, 0))
        pygame.draw.circle(surface, dark_color, (cx, cy + 8), radius, 2)

        # Блик (светлее)
        highlight = (min(self.color[0] + 80, 255),
                     min(self.color[1] + 80, 255),
                     min(self.color[2] + 80, 255))
        pygame.draw.circle(surface, highlight,
                           (cx - radius // 3, cy - radius // 4 + 8),
                           radius // 3)

        # Маленький блик
        pygame.draw.circle(surface, WHITE,
                           (cx - radius // 2, cy - radius // 3 + 8),
                           radius // 6)

        # Глаза
        eye_y = cy + 3
        eye_radius = 6
        # Белки
        pygame.draw.circle(surface, WHITE, (cx - 10, eye_y), eye_radius)
        pygame.draw.circle(surface, WHITE, (cx + 10, eye_y), eye_radius)
        # Зрачки
        pygame.draw.circle(surface, BLACK, (cx - 10, eye_y + 2), 3)
        pygame.draw.circle(surface, BLACK, (cx + 10, eye_y + 2), 3)
        # Блики в глазах
        pygame.draw.circle(surface, WHITE, (cx - 8, eye_y - 1), 2)
        pygame.draw.circle(surface, WHITE, (cx + 12, eye_y - 1), 2)

        # Рот (милая улыбка или овал)
        pygame.draw.ellipse(surface, (200, 100, 100),
                            (cx - 5, cy + 15, 10, 6))

    def _draw_skeleton(self, surface, rect):
        """Красивая отрисовка скелета на карте"""
        cx = rect.centerx
        cy = rect.centery

        # Голова (череп)
        skull_radius = 14
        skull_y = rect.top + 18
        pygame.draw.circle(surface, self.color, (cx, skull_y), skull_radius)
        pygame.draw.circle(surface, (100, 100, 100), (cx, skull_y), skull_radius, 2)

        # Глазницы
        pygame.draw.circle(surface, BLACK, (cx - 6, skull_y - 2), 5)
        pygame.draw.circle(surface, BLACK, (cx + 6, skull_y - 2), 5)
        # Красное свечение
        pygame.draw.circle(surface, RED, (cx - 6, skull_y - 2), 3)
        pygame.draw.circle(surface, RED, (cx + 6, skull_y - 2), 3)
        # Яркие точки
        pygame.draw.circle(surface, (255, 150, 150), (cx - 5, skull_y - 3), 1)
        pygame.draw.circle(surface, (255, 150, 150), (cx + 7, skull_y - 3), 1)

        # Нос
        pygame.draw.polygon(surface, BLACK, [
            (cx, skull_y + 2),
            (cx - 3, skull_y + 7),
            (cx + 3, skull_y + 7)
        ])

        # Зубы
        teeth_y = skull_y + 9
        for i in range(-2, 3):
            pygame.draw.rect(surface, self.color,
                             (cx + i * 5 - 2, teeth_y, 4, 6))
            pygame.draw.rect(surface, (120, 120, 120),
                             (cx + i * 5 - 2, teeth_y, 4, 6), 1)

        # Позвоночник
        spine_top = skull_y + skull_radius
        spine_bottom = rect.bottom - 20
        pygame.draw.line(surface, self.color, (cx, spine_top), (cx, spine_bottom), 4)

        # Рёбра
        for i in range(3):
            rib_y = spine_top + 8 + i * 10
            pygame.draw.line(surface, self.color, (cx - 15, rib_y + 3), (cx, rib_y), 3)
            pygame.draw.line(surface, self.color, (cx + 15, rib_y + 3), (cx, rib_y), 3)

        # Руки
        arm_y = spine_top + 5
        pygame.draw.line(surface, self.color, (cx, arm_y), (cx - 22, cy + 10), 3)
        pygame.draw.line(surface, self.color, (cx, arm_y), (cx + 22, cy + 10), 3)
        # Кисти
        pygame.draw.circle(surface, self.color, (cx - 24, cy + 12), 5)
        pygame.draw.circle(surface, self.color, (cx + 24, cy + 12), 5)

        # Ноги
        pygame.draw.line(surface, self.color, (cx, spine_bottom), (cx - 10, rect.bottom - 5), 3)
        pygame.draw.line(surface, self.color, (cx, spine_bottom), (cx + 10, rect.bottom - 5), 3)
        # Стопы
        pygame.draw.ellipse(surface, self.color, (cx - 16, rect.bottom - 8, 12, 6))
        pygame.draw.ellipse(surface, self.color, (cx + 4, rect.bottom - 8, 12, 6))

    def _draw_generic(self, surface, rect):
        """Универсальная отрисовка врага"""
        pygame.draw.rect(surface, self.color, rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)

        cx, cy = rect.centerx, rect.centery - 5
        # Злые глаза
        pygame.draw.circle(surface, WHITE, (cx - 10, cy), 6)
        pygame.draw.circle(surface, WHITE, (cx + 10, cy), 6)
        pygame.draw.circle(surface, RED, (cx - 10, cy + 1), 3)
        pygame.draw.circle(surface, RED, (cx + 10, cy + 1), 3)

    def _draw_health_bar(self, surface, rect):
        """Отрисовка полоски здоровья"""
        bar_width = self.size
        bar_height = 8
        bar_x = rect.x
        bar_y = rect.y - 14

        # Фон (красный)
        pygame.draw.rect(surface, (100, 30, 30), (bar_x, bar_y, bar_width, bar_height), border_radius=3)

        # Здоровье (зелёный)
        hp_width = int(bar_width * (self.hp / self.max_hp))
        if hp_width > 0:
            # Градиент от зелёного к жёлтому при низком HP
            hp_ratio = self.hp / self.max_hp
            if hp_ratio > 0.5:
                hp_color = GREEN
            elif hp_ratio > 0.25:
                hp_color = YELLOW
            else:
                hp_color = ORANGE
            pygame.draw.rect(surface, hp_color, (bar_x, bar_y, hp_width, bar_height), border_radius=3)

        # Рамка
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)