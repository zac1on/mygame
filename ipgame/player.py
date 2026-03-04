# player.py
import pygame
import os
from settings import *


class Player:
    def __init__(self, x, y):
        # УВЕЛИЧЕННЫЙ размер персонажа
        self.size = TILE_SIZE + 16  # Было: TILE_SIZE - 8, стало больше
        self.rect = pygame.Rect(x * TILE_SIZE - 8, y * TILE_SIZE - 8,
                                self.size, self.size)

        # Загрузка спрайтов
        self.sprites = {}
        self.use_sprite = False
        self._load_sprites()

        # Характеристики
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.max_mana = PLAYER_MAX_MANA
        self.mana = self.max_mana
        self.base_attack = PLAYER_BASE_ATTACK
        self.base_defense = PLAYER_BASE_DEFENSE
        self.level = 1
        self.exp = 0
        self.exp_to_next = 50
        self.gold = 20
        self.speed = PLAYER_SPEED

        # Экипировка
        self.weapon = None
        self.armor = None

        # Направление
        self.direction = "down"
        self.moving = False

        # Анимация
        self.anim_timer = 0
        self.anim_frame = 0

    def _load_sprites(self):
        """Загрузка спрайтов игрока"""
        sprite_paths = {
            "down": ["assets/player.png", "assets/player_down.png"],
            "up": ["assets/player_up.png", "assets/player.png"],
            "left": ["assets/player_left.png", "assets/player.png"],
            "right": ["assets/player_right.png", "assets/player.png"],
        }

        for direction, paths in sprite_paths.items():
            for path in paths:
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        # УВЕЛИЧЕННЫЙ размер спрайта - делаем его больше
                        sprite = pygame.transform.scale(sprite, (self.size, self.size))
                        self.sprites[direction] = sprite
                        self.use_sprite = True
                        print(f"✅ Загружен спрайт: {path} (размер: {self.size}x{self.size})")
                        break
                    except Exception as e:
                        print(f"❌ Ошибка загрузки {path}: {e}")

        if self.sprites:
            default_sprite = list(self.sprites.values())[0]
            for direction in ["down", "up", "left", "right"]:
                if direction not in self.sprites:
                    self.sprites[direction] = default_sprite

        if self.use_sprite:
            print(f"🎮 Используются спрайты игрока (размер: {self.size}x{self.size})")
        else:
            print(f"🎨 Используется стандартная отрисовка")

    @property
    def attack(self):
        bonus = 0
        if self.weapon and self.weapon in ITEMS:
            bonus = ITEMS[self.weapon].get("attack", 0)
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = 0
        if self.armor and self.armor in ITEMS:
            bonus = ITEMS[self.armor].get("defense", 0)
        return self.base_defense + bonus

    def gain_exp(self, amount):
        self.exp += amount
        leveled_up = False
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.5)
            self.max_hp += 15
            self.hp = self.max_hp
            self.max_mana += 8
            self.mana = self.max_mana
            self.base_attack += 3
            self.base_defense += 2
            leveled_up = True
        return leveled_up

    def move(self, dx, dy, walls):
        self.moving = (dx != 0 or dy != 0)

        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        if dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        # Используем меньший хитбокс для коллизий
        collision_rect = self.rect.inflate(-20, -20)

        new_rect = collision_rect.move(dx * self.speed, 0)
        if not self._check_collision(new_rect, walls):
            self.rect.x += dx * self.speed

        new_rect = collision_rect.move(0, dy * self.speed)
        if not self._check_collision(new_rect, walls):
            self.rect.y += dy * self.speed

    def _check_collision(self, rect, walls):
        for wall in walls:
            if rect.colliderect(wall):
                return True
        return False

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def restore_mana(self, amount):
        self.mana = min(self.mana + amount, self.max_mana)

    def draw(self, surface, camera):
        draw_rect = camera.apply(self.rect)

        # Используем спрайт если загружен
        if self.use_sprite and self.direction in self.sprites:
            sprite = self.sprites[self.direction]
            surface.blit(sprite, draw_rect)

            # Добавим тень под персонажем для глубины
            shadow_surf = pygame.Surface((self.size - 10, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
            shadow_pos = (draw_rect.centerx - (self.size - 10) // 2,
                          draw_rect.bottom - 4)
            surface.blit(shadow_surf, shadow_pos)
        else:
            # Стандартная отрисовка (УВЕЛИЧЕННАЯ)
            self._draw_default(surface, draw_rect)

        # Меч (если есть оружие)
        if self.weapon:
            self._draw_weapon(surface, draw_rect)

    def _draw_default(self, surface, draw_rect):
        """Стандартная отрисовка без спрайта (УВЕЛИЧЕННАЯ)"""
        # Тело
        body_color = (60, 120, 200)
        pygame.draw.rect(surface, body_color, draw_rect, border_radius=10)

        # Обводка
        pygame.draw.rect(surface, (40, 80, 160), draw_rect, 2, border_radius=10)

        # Глаза (КРУПНЕЕ)
        eye_size = 8  # Было 6
        cx, cy = draw_rect.centerx, draw_rect.centery - 8

        if self.direction == "down":
            # Глаза
            pygame.draw.circle(surface, WHITE, (cx - 12, cy), eye_size)
            pygame.draw.circle(surface, WHITE, (cx + 12, cy), eye_size)
            pygame.draw.circle(surface, BLACK, (cx - 12, cy + 2), 4)
            pygame.draw.circle(surface, BLACK, (cx + 12, cy + 2), 4)
            # Блики в глазах
            pygame.draw.circle(surface, WHITE, (cx - 10, cy - 1), 2)
            pygame.draw.circle(surface, WHITE, (cx + 14, cy - 1), 2)

        elif self.direction == "up":
            pygame.draw.circle(surface, WHITE, (cx - 12, cy - 5), eye_size)
            pygame.draw.circle(surface, WHITE, (cx + 12, cy - 5), eye_size)
            pygame.draw.circle(surface, BLACK, (cx - 12, cy - 7), 4)
            pygame.draw.circle(surface, BLACK, (cx + 12, cy - 7), 4)

        elif self.direction == "left":
            pygame.draw.circle(surface, WHITE, (cx - 15, cy), eye_size)
            pygame.draw.circle(surface, BLACK, (cx - 17, cy), 4)
            pygame.draw.circle(surface, WHITE, (cx - 14, cy - 2), 2)

        elif self.direction == "right":
            pygame.draw.circle(surface, WHITE, (cx + 15, cy), eye_size)
            pygame.draw.circle(surface, BLACK, (cx + 17, cy), 4)
            pygame.draw.circle(surface, WHITE, (cx + 18, cy - 2), 2)

        # Улыбка
        if self.direction == "down":
            pygame.draw.arc(surface, BLACK,
                            (cx - 10, cy + 8, 20, 12),
                            3.14, 6.28, 2)

    def _draw_weapon(self, surface, draw_rect):
        """Отрисовка оружия (УВЕЛИЧЕННАЯ)"""
        sword_color = ITEMS[self.weapon]["color"]
        sword_width = 4  # Толще меч

        if self.direction == "right":
            # Рукоять
            pygame.draw.line(surface, (139, 69, 19),
                             (draw_rect.right, draw_rect.centery),
                             (draw_rect.right + 8, draw_rect.centery - 8), sword_width + 2)
            # Клинок
            pygame.draw.line(surface, sword_color,
                             (draw_rect.right + 8, draw_rect.centery - 8),
                             (draw_rect.right + 22, draw_rect.centery - 22), sword_width)
            # Гарда
            pygame.draw.line(surface, GOLD,
                             (draw_rect.right + 4, draw_rect.centery - 4),
                             (draw_rect.right + 12, draw_rect.centery - 12), 2)

        elif self.direction == "left":
            pygame.draw.line(surface, (139, 69, 19),
                             (draw_rect.left, draw_rect.centery),
                             (draw_rect.left - 8, draw_rect.centery - 8), sword_width + 2)
            pygame.draw.line(surface, sword_color,
                             (draw_rect.left - 8, draw_rect.centery - 8),
                             (draw_rect.left - 22, draw_rect.centery - 22), sword_width)
            pygame.draw.line(surface, GOLD,
                             (draw_rect.left - 4, draw_rect.centery - 4),
                             (draw_rect.left - 12, draw_rect.centery - 12), 2)

        elif self.direction == "down":
            pygame.draw.line(surface, (139, 69, 19),
                             (draw_rect.right - 8, draw_rect.bottom),
                             (draw_rect.right + 2, draw_rect.bottom + 10), sword_width + 2)
            pygame.draw.line(surface, sword_color,
                             (draw_rect.right + 2, draw_rect.bottom + 10),
                             (draw_rect.right + 12, draw_rect.bottom + 20), sword_width)
            pygame.draw.line(surface, GOLD,
                             (draw_rect.right - 4, draw_rect.bottom + 5),
                             (draw_rect.right + 6, draw_rect.bottom + 15), 2)

        elif self.direction == "up":
            pygame.draw.line(surface, (139, 69, 19),
                             (draw_rect.right - 8, draw_rect.top),
                             (draw_rect.right + 2, draw_rect.top - 10), sword_width + 2)
            pygame.draw.line(surface, sword_color,
                             (draw_rect.right + 2, draw_rect.top - 10),
                             (draw_rect.right + 12, draw_rect.top - 20), sword_width)
            pygame.draw.line(surface, GOLD,
                             (draw_rect.right - 4, draw_rect.top - 5),
                             (draw_rect.right + 6, draw_rect.top - 15), 2)