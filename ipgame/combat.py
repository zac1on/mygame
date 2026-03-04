# combat.py
import pygame
import random
import os
from settings import *
from button import Button, ButtonGroup, Panel, HealthBar


class CombatSystem:
    def __init__(self):
        self.in_combat = False
        self.current_enemy = None
        self.player_turn = True
        self.combat_log = []
        self.max_log = 5
        self.action_cooldown = 0
        self.defending = False

        self.buttons = ButtonGroup()
        self.damage_texts = []

        self.player_shake = 0
        self.enemy_shake = 0

        # Спрайты
        self.player_combat_sprite = None
        self.enemy_sprites = {}
        self._load_combat_sprites()

    def _load_combat_sprites(self):
        paths = ["assets/player.png", "assets/player_down.png"]
        for path in paths:
            if os.path.exists(path):
                try:
                    self.player_combat_sprite = pygame.image.load(path).convert_alpha()
                    break
                except:
                    pass

        enemy_files = {
            "slime": ["assets/enemy_slime.png", "assets/slime.png"],
            "skeleton": ["assets/enemy_skeleton.png", "assets/skeleton.png"],
        }

        for etype, paths in enemy_files.items():
            for path in paths:
                if os.path.exists(path):
                    try:
                        self.enemy_sprites[etype] = pygame.image.load(path).convert_alpha()
                        break
                    except:
                        pass

    def start_combat(self, enemy):
        self.in_combat = True
        self.current_enemy = enemy
        self.player_turn = True
        self.combat_log = ["Бой начался!"]
        self.action_cooldown = 30
        self.defending = False

    def handle_input(self, event, player):
        if not self.in_combat or not self.player_turn or self.action_cooldown > 0:
            return None

        actions = ["attack", "defend", "magic", "flee"]

        # Клик мыши
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, btn in enumerate(self.buttons.buttons):
                if btn.check_click(mouse_pos):
                    return self._execute_action(actions[i], player)

        # Клавиатура
        if event.type == pygame.KEYDOWN:
            # Навигация
            result = self.buttons.handle_keyboard(event.key)
            if result is not None:
                return self._execute_action(actions[result], player)

            # Быстрые клавиши
            key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}
            if event.key in key_map:
                idx = key_map[event.key]
                self.buttons.selected_index = idx
                return self._execute_action(actions[idx], player)

        return None

    def _execute_action(self, action, player):
        result = None
        self.defending = False

        if action == "attack":
            damage = max(player.attack - self.current_enemy.defense + random.randint(-3, 3), 1)
            actual = self.current_enemy.take_damage(damage + self.current_enemy.defense)
            self._add_log(f"Вы нанесли {actual} урона!")
            self.enemy_shake = 15
            self.damage_texts.append(("enemy", f"-{actual}", 60, RED))

            if not self.current_enemy.alive:
                exp = self.current_enemy.exp_reward
                gold = self.current_enemy.gold_reward
                player.gold += gold
                leveled = player.gain_exp(exp)
                self._add_log(f"Победа! +{exp} EXP, +{gold} G")
                if leveled:
                    self._add_log(f"Уровень повышен до {player.level}!")
                self.in_combat = False
                return "victory"

        elif action == "defend":
            self.defending = True
            self._add_log("Вы приняли защитную стойку!")

        elif action == "magic":
            if player.mana >= 15:
                player.mana -= 15
                damage = int(player.attack * 1.8) + random.randint(2, 8)
                actual = self.current_enemy.take_damage(damage + self.current_enemy.defense)
                self._add_log(f"Магия! {actual} урона! (-15 MP)")
                self.enemy_shake = 20
                self.damage_texts.append(("enemy", f"-{actual}", 60, PURPLE))

                if not self.current_enemy.alive:
                    exp = self.current_enemy.exp_reward
                    gold = self.current_enemy.gold_reward
                    player.gold += gold
                    player.gain_exp(exp)
                    self._add_log(f"Победа! +{exp} EXP, +{gold} G")
                    self.in_combat = False
                    return "victory"
            else:
                self._add_log("Недостаточно маны!")
                return None

        elif action == "flee":
            if random.random() < 0.5:
                self._add_log("Вы сбежали!")
                self.in_combat = False
                return "fled"
            else:
                self._add_log("Не удалось сбежать!")

        self.player_turn = False
        self.action_cooldown = 40
        return result

    def update(self, player):
        if not self.in_combat:
            return

        if self.action_cooldown > 0:
            self.action_cooldown -= 1

        if self.player_shake > 0:
            self.player_shake -= 1
        if self.enemy_shake > 0:
            self.enemy_shake -= 1

        # Обновление текстов урона
        self.damage_texts = [(t, txt, timer - 1, c) for t, txt, timer, c in self.damage_texts if timer > 0]

        # Ход врага
        if not self.player_turn and self.action_cooldown <= 0:
            damage = max(self.current_enemy.attack - player.defense + random.randint(-2, 2), 1)

            if self.defending:
                damage = max(damage // 2, 1)
                self._add_log(f"Блок! Получено {damage} урона")
            else:
                self._add_log(f"Враг нанёс {damage} урона!")

            player.hp -= damage
            self.player_shake = 15
            self.damage_texts.append(("player", f"-{damage}", 60, ORANGE))

            if player.hp <= 0:
                player.hp = 0
                self._add_log("Вы повержены...")
                self.in_combat = False
                return

            self.player_turn = True
            self.action_cooldown = 20
            self.defending = False

    def _add_log(self, text):
        self.combat_log.append(text)
        if len(self.combat_log) > self.max_log:
            self.combat_log.pop(0)

    def draw(self, surface, player):
        if not self.in_combat:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Затемнение
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        scale = min(screen_w / 1024, screen_h / 768)
        scale = max(0.6, min(scale, 1.5))

        # Заголовок
        title_font = pygame.font.SysFont("Arial", int(36 * scale), bold=True)
        title = title_font.render("⚔ БОЙ ⚔", True, RED)
        surface.blit(title, title.get_rect(centerx=screen_w // 2, y=int(20 * scale)))

        # Область боя
        combat_area_y = int(80 * scale)
        combat_area_h = int(280 * scale)

        # Игрок (слева)
        player_x = int(screen_w * 0.25)
        player_y = combat_area_y + combat_area_h // 2
        if self.player_shake > 0:
            player_x += random.randint(-4, 4)
            player_y += random.randint(-2, 2)

        self._draw_combatant(surface, player_x, player_y, scale, "player", player)

        # Враг (справа)
        enemy_x = int(screen_w * 0.75)
        enemy_y = combat_area_y + combat_area_h // 2
        if self.enemy_shake > 0:
            enemy_x += random.randint(-4, 4)
            enemy_y += random.randint(-2, 2)

        self._draw_combatant(surface, enemy_x, enemy_y, scale, "enemy", self.current_enemy)

        # Тексты урона
        dmg_font = pygame.font.SysFont("Arial", int(28 * scale), bold=True)
        for target, text, timer, color in self.damage_texts:
            x = player_x if target == "player" else enemy_x
            y = combat_area_y + int(50 * scale) - (60 - timer)
            alpha = min(255, timer * 6)
            surf = dmg_font.render(text, True, color)
            surface.blit(surf, (x - surf.get_width() // 2, y))

        # Лог боя
        log_panel = Panel(
            int(50 * scale), combat_area_y + combat_area_h + int(20 * scale),
                             screen_w - int(100 * scale), int(100 * scale),
            bg_color=(25, 30, 45)
        )
        log_panel.draw(surface)

        log_font = pygame.font.SysFont("Arial", int(16 * scale))
        log_y = combat_area_y + combat_area_h + int(35 * scale)
        for i, log_text in enumerate(self.combat_log[-4:]):
            color = WHITE if i == len(self.combat_log[-4:]) - 1 else LIGHT_GRAY
            surf = log_font.render(log_text, True, color)
            surface.blit(surf, (int(70 * scale), log_y + i * int(20 * scale)))

        # Индикатор хода
        turn_font = pygame.font.SysFont("Arial", int(18 * scale), bold=True)
        turn_text = "▶ ВАШ ХОД" if self.player_turn else "▶ ХОД ВРАГА"
        turn_color = GREEN if self.player_turn else RED
        turn_surf = turn_font.render(turn_text, True, turn_color)
        surface.blit(turn_surf, turn_surf.get_rect(
            right=screen_w - int(70 * scale),
            y=combat_area_y + combat_area_h + int(35 * scale)
        ))

        # Кнопки действий
        self._draw_action_buttons(surface, scale)

    def _draw_combatant(self, surface, x, y, scale, combatant_type, entity):
        """Отрисовка участника боя"""
        size = int(100 * scale)

        # Тень/платформа
        shadow = pygame.Surface((int(80 * scale), int(20 * scale)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), shadow.get_rect())
        surface.blit(shadow, (x - int(40 * scale), y + size // 2))

        if combatant_type == "player":
            if self.player_combat_sprite:
                sprite = pygame.transform.scale(self.player_combat_sprite, (size, size))
                surface.blit(sprite, (x - size // 2, y - size // 2))
            else:
                self._draw_default_player(surface, x, y, size)

            # HP/MP бары
            bar_y = y + size // 2 + int(30 * scale)
            hp_bar = HealthBar(x - int(60 * scale), bar_y, int(120 * scale), int(16 * scale),
                               entity.max_hp, entity.hp)
            hp_bar.draw(surface, "HP")

            mp_bar = HealthBar(x - int(60 * scale), bar_y + int(24 * scale),
                               int(120 * scale), int(16 * scale),
                               entity.max_mana, entity.mana)
            mp_bar.draw(surface, "MP")
            # Перекрасить в синий
            ratio = entity.mana / entity.max_mana if entity.max_mana > 0 else 0
            fill = pygame.Rect(x - int(58 * scale), bar_y + int(26 * scale),
                               int((116 * scale) * ratio), int(12 * scale))
            pygame.draw.rect(surface, BLUE, fill, border_radius=3)

            # Имя
            font = pygame.font.SysFont("Arial", int(16 * scale), bold=True)
            name = font.render(f"Герой Lv.{entity.level}", True, WHITE)
            surface.blit(name, name.get_rect(centerx=x, y=bar_y + int(50 * scale)))

            # Индикатор защиты
            if self.defending:
                shield_font = pygame.font.SysFont("Arial", int(30 * scale))
                shield = shield_font.render("🛡", True, BLUE)
                surface.blit(shield, (x - 15, y - size // 2 - int(35 * scale)))

        else:  # enemy
            enemy = entity
            if enemy.type in self.enemy_sprites:
                sprite = pygame.transform.scale(self.enemy_sprites[enemy.type], (size, size))
                surface.blit(sprite, (x - size // 2, y - size // 2))
            else:
                self._draw_default_enemy(surface, x, y, size, enemy)

            # HP бар
            bar_y = y + size // 2 + int(30 * scale)
            hp_bar = HealthBar(x - int(60 * scale), bar_y, int(120 * scale), int(16 * scale),
                               enemy.max_hp, enemy.hp)
            hp_bar.draw(surface, "HP")

            # Имя
            font = pygame.font.SysFont("Arial", int(16 * scale), bold=True)
            name = font.render(enemy.type.capitalize(), True, WHITE)
            surface.blit(name, name.get_rect(centerx=x, y=bar_y + int(25 * scale)))

    def _draw_default_player(self, surface, x, y, size):
        """Стандартная отрисовка игрока"""
        # Тело
        body = pygame.Rect(x - size // 3, y - size // 4, size * 2 // 3, size * 3 // 4)
        pygame.draw.rect(surface, (60, 120, 200), body, border_radius=10)

        # Голова
        head_r = size // 4
        pygame.draw.circle(surface, (255, 220, 180), (x, y - size // 4), head_r)

        # Глаза
        pygame.draw.circle(surface, WHITE, (x - 8, y - size // 4 - 2), 6)
        pygame.draw.circle(surface, WHITE, (x + 8, y - size // 4 - 2), 6)
        pygame.draw.circle(surface, (50, 80, 150), (x - 8, y - size // 4), 3)
        pygame.draw.circle(surface, (50, 80, 150), (x + 8, y - size // 4), 3)

    def _draw_default_enemy(self, surface, x, y, size, enemy):
        """Стандартная отрисовка врага"""
        if enemy.type == "slime":
            radius = size // 2 - 5
            pygame.draw.circle(surface, enemy.color, (x, y + 10), radius)
            pygame.draw.circle(surface, WHITE, (x - 12, y + 5), 8)
            pygame.draw.circle(surface, WHITE, (x + 12, y + 5), 8)
            pygame.draw.circle(surface, BLACK, (x - 12, y + 7), 4)
            pygame.draw.circle(surface, BLACK, (x + 12, y + 7), 4)
        else:
            pygame.draw.circle(surface, enemy.color, (x, y - size // 4), size // 4)
            pygame.draw.line(surface, enemy.color, (x, y - size // 4 + 15), (x, y + size // 4), 4)
            pygame.draw.circle(surface, RED, (x - 8, y - size // 4 - 3), 4)
            pygame.draw.circle(surface, RED, (x + 8, y - size // 4 - 3), 4)

    def _draw_action_buttons(self, surface, scale):
        """Отрисовка кнопок действий"""
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        btn_width = int(170 * scale)
        btn_height = int(50 * scale)
        btn_spacing = int(15 * scale)

        start_x = (screen_w - btn_width * 2 - btn_spacing) // 2
        start_y = screen_h - int(130 * scale)

        actions = [
            ("[1] Атака", (180, 60, 60)),
            ("[2] Защита", (60, 100, 180)),
            ("[3] Магия", (140, 60, 180)),
            ("[4] Бегство", (180, 150, 50)),
        ]

        self.buttons = ButtonGroup()

        for i, (text, color) in enumerate(actions):
            col = i % 2
            row = i // 2
            x = start_x + col * (btn_width + btn_spacing)
            y = start_y + row * (btn_height + btn_spacing)

            btn = Button(x, y, btn_width, btn_height, text,
                         color=color if self.player_turn else DARK_GRAY,
                         font_size=int(18 * scale))
            self.buttons.add_button(btn)

        if self.player_turn and self.action_cooldown <= 0:
            self.buttons.update(pygame.mouse.get_pos())

        self.buttons.draw(surface)