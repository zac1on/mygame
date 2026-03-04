# ui.py
import pygame
from settings import *
from button import Button, ButtonGroup, Panel, HealthBar


class UI:
    def __init__(self):
        self.message = None
        self.message_timer = 0

    def init_fonts(self):
        pass

    def show_message(self, text, duration=120):
        self.message = text
        self.message_timer = duration

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = None

    def draw_hud(self, surface, player):
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        scale = min(screen_w / 1024, screen_h / 768)
        scale = max(0.7, min(scale, 1.5))

        panel_width = int(280 * scale)
        panel_height = int(120 * scale)
        padding = int(15 * scale)

        panel = Panel(padding, padding, panel_width, panel_height, bg_color=(30, 40, 60))
        panel.draw(surface)

        bar_width = int(180 * scale)
        bar_height = int(18 * scale)
        x_start = padding + int(55 * scale)
        y_start = padding + int(15 * scale)

        # HP
        hp_bar = HealthBar(x_start, y_start, bar_width, bar_height, player.max_hp, player.hp)
        hp_bar.draw(surface, "HP")

        # MP
        mp_y = y_start + bar_height + int(8 * scale)
        mp_bar = HealthBar(x_start, mp_y, bar_width, bar_height, player.max_mana, player.mana)
        mp_bar.draw(surface, "MP", bar_color=BLUE)

        # EXP
        exp_y = mp_y + bar_height + int(8 * scale)
        exp_bar = HealthBar(x_start, exp_y, bar_width, int(12 * scale), player.exp_to_next, player.exp)
        exp_bar.draw(surface, "EXP", bar_color=PURPLE)

        # Статы
        info_y = exp_y + int(20 * scale)
        font = pygame.font.SysFont("Arial", int(14 * scale), bold=True)

        stats = f"Lv.{player.level}  💰{player.gold}  ⚔{player.attack}  🛡{player.defense}"
        stats_surf = font.render(stats, True, GOLD)
        surface.blit(stats_surf, (padding + int(10 * scale), info_y))

    def draw_message(self, surface):
        if not self.message:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()
        scale = min(screen_w / 1024, screen_h / 768)

        font = pygame.font.SysFont("Arial", int(20 * scale), bold=True)
        text_surf = font.render(self.message, True, WHITE)

        padding = 20
        msg_rect = text_surf.get_rect(centerx=screen_w // 2, y=screen_h // 2 - 80)
        bg_rect = msg_rect.inflate(padding * 2, padding)

        pygame.draw.rect(surface, (30, 40, 60), bg_rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, bg_rect, 3, border_radius=10)
        surface.blit(text_surf, msg_rect)

    def draw_dialogue(self, surface, npc_name, text, page, total_pages):
        screen_w = surface.get_width()
        screen_h = surface.get_height()
        scale = min(screen_w / 1024, screen_h / 768)

        width = int(700 * scale)
        height = int(160 * scale)
        x = (screen_w - width) // 2
        y = screen_h - height - int(40 * scale)

        panel = Panel(x, y, width, height, bg_color=(30, 40, 60))
        panel.draw(surface)

        name_font = pygame.font.SysFont("Arial", int(20 * scale), bold=True)
        name_surf = name_font.render(npc_name, True, GOLD)
        name_bg = name_surf.get_rect(topleft=(x + 20, y + 15)).inflate(16, 8)
        pygame.draw.rect(surface, (40, 50, 70), name_bg, border_radius=6)
        pygame.draw.rect(surface, GOLD, name_bg, 2, border_radius=6)
        surface.blit(name_surf, (x + 28, y + 19))

        text_font = pygame.font.SysFont("Arial", int(18 * scale))
        text_surf = text_font.render(text, True, WHITE)
        surface.blit(text_surf, (x + 25, y + 60))

        hint_font = pygame.font.SysFont("Arial", int(14 * scale))
        hint = hint_font.render(f"[{page + 1}/{total_pages}]  Нажмите E или Enter", True, LIGHT_GRAY)
        surface.blit(hint, (x + 25, y + height - 35))


class PauseMenu:
    def __init__(self):
        self.visible = False
        self.buttons = ButtonGroup()
        self.options = ["Продолжить", "Настройки", "Сохранить", "Выйти"]
        self.selected_index = 0

    def toggle(self):
        self.visible = not self.visible
        self.selected_index = 0

    def handle_input(self, event, screen_size):
        if not self.visible:
            return None

        screen_w, screen_h = screen_size
        scale = min(screen_w / 1024, screen_h / 768)

        btn_width = int(250 * scale)
        btn_height = int(50 * scale)
        btn_spacing = int(15 * scale)
        panel_y = (screen_h - int(320 * scale)) // 2
        start_y = panel_y + int(70 * scale)

        # Клик мыши
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i in range(len(self.options)):
                btn_y = start_y + i * (btn_height + btn_spacing)
                btn_rect = pygame.Rect((screen_w - btn_width) // 2, btn_y, btn_width, btn_height)
                if btn_rect.collidepoint(mouse_pos):
                    return self.options[i]

        # Клавиатура
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index]
            elif event.key == pygame.K_ESCAPE:
                self.visible = False

        return None

    def draw(self, surface):
        if not self.visible:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Затемнение
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        scale = min(screen_w / 1024, screen_h / 768)

        panel_width = int(350 * scale)
        panel_height = int(320 * scale)
        panel_x = (screen_w - panel_width) // 2
        panel_y = (screen_h - panel_height) // 2

        panel = Panel(panel_x, panel_y, panel_width, panel_height)
        panel.draw(surface, "⏸ ПАУЗА")

        btn_width = int(250 * scale)
        btn_height = int(50 * scale)
        btn_spacing = int(15 * scale)
        start_y = panel_y + int(70 * scale)

        colors = [(50, 150, 50), (50, 100, 180), (180, 150, 50), (180, 50, 50)]
        mouse_pos = pygame.mouse.get_pos()

        for i, (option, color) in enumerate(zip(self.options, colors)):
            btn_y = start_y + i * (btn_height + btn_spacing)
            btn_rect = pygame.Rect((screen_w - btn_width) // 2, btn_y, btn_width, btn_height)

            is_hovered = btn_rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_index)

            if is_hovered:
                self.selected_index = i

            btn = Button(btn_rect.x, btn_rect.y, btn_width, btn_height, option,
                         color=color, font_size=int(20 * scale))
            btn.is_hovered = is_hovered
            btn.is_selected = is_selected
            btn.draw(surface)


class SettingsMenu:
    def __init__(self, game_settings):
        self.visible = False
        self.settings = game_settings
        self.selected_index = 0

        self.options = [
            ("fullscreen", "Полный экран"),
            ("resolution", "Разрешение"),
            ("music_volume", "Музыка"),
            ("sfx_volume", "Звуки"),
            ("show_fps", "Показать FPS"),
            ("show_minimap", "Миникарта"),
        ]

    def toggle(self):
        self.visible = not self.visible
        self.selected_index = 0

    def _get_value_text(self, key):
        if key == "fullscreen":
            return "ВКЛ" if self.settings.fullscreen else "ВЫКЛ"
        elif key == "resolution":
            w, h = self.settings.get_resolution()
            return f"{w}x{h}"
        elif key == "music_volume":
            return f"{self.settings.music_volume}%"
        elif key == "sfx_volume":
            return f"{self.settings.sfx_volume}%"
        elif key == "show_fps":
            return "ВКЛ" if self.settings.show_fps else "ВЫКЛ"
        elif key == "show_minimap":
            return "ВКЛ" if self.settings.show_minimap else "ВЫКЛ"
        return ""

    def _change_option(self, key, direction=1):
        if key == "fullscreen":
            self.settings.fullscreen = not self.settings.fullscreen
        elif key == "resolution":
            if direction > 0:
                self.settings.next_resolution()
            else:
                self.settings.prev_resolution()
        elif key == "music_volume":
            self.settings.music_volume = max(0, min(100, self.settings.music_volume + direction * 10))
        elif key == "sfx_volume":
            self.settings.sfx_volume = max(0, min(100, self.settings.sfx_volume + direction * 10))
        elif key == "show_fps":
            self.settings.show_fps = not self.settings.show_fps
        elif key == "show_minimap":
            self.settings.show_minimap = not self.settings.show_minimap

    def handle_input(self, event, screen_size):
        if not self.visible:
            return None

        screen_w, screen_h = screen_size
        scale = min(screen_w / 1024, screen_h / 768)

        panel_width = int(500 * scale)
        panel_height = int(450 * scale)
        panel_x = (screen_w - panel_width) // 2
        panel_y = (screen_h - panel_height) // 2

        btn_width = int(420 * scale)
        btn_height = int(40 * scale)
        start_y = panel_y + int(60 * scale)
        spacing = int(10 * scale)

        action_btn_width = int(180 * scale)
        action_btn_height = int(45 * scale)
        action_y = panel_y + panel_height - int(70 * scale)

        # Клик мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Кнопки настроек
            for i in range(len(self.options)):
                row_y = start_y + i * (btn_height + spacing)
                row_rect = pygame.Rect(panel_x + 40, row_y, btn_width, btn_height)
                if row_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    if event.button == 1:  # ЛКМ
                        self._change_option(self.options[i][0], 1)
                    elif event.button == 3:  # ПКМ
                        self._change_option(self.options[i][0], -1)
                    return None

            # Кнопка "Применить"
            apply_rect = pygame.Rect(panel_x + panel_width // 2 - action_btn_width - 15,
                                     action_y, action_btn_width, action_btn_height)
            if apply_rect.collidepoint(mouse_pos) and event.button == 1:
                self.settings.save()
                return "apply"

            # Кнопка "Назад"
            back_rect = pygame.Rect(panel_x + panel_width // 2 + 15,
                                    action_y, action_btn_width, action_btn_height)
            if back_rect.collidepoint(mouse_pos) and event.button == 1:
                self.visible = False
                return "back"

        # Клавиатура
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._change_option(self.options[self.selected_index][0], -1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._change_option(self.options[self.selected_index][0], 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._change_option(self.options[self.selected_index][0], 1)
            elif event.key == pygame.K_ESCAPE:
                self.visible = False
                return "back"

        return None

    def draw(self, surface):
        if not self.visible:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        scale = min(screen_w / 1024, screen_h / 768)

        panel_width = int(500 * scale)
        panel_height = int(450 * scale)
        panel_x = (screen_w - panel_width) // 2
        panel_y = (screen_h - panel_height) // 2

        panel = Panel(panel_x, panel_y, panel_width, panel_height)
        panel.draw(surface, "⚙ НАСТРОЙКИ")

        btn_width = int(420 * scale)
        btn_height = int(40 * scale)
        start_y = panel_y + int(60 * scale)
        spacing = int(10 * scale)

        font = pygame.font.SysFont("Arial", int(18 * scale), bold=True)
        mouse_pos = pygame.mouse.get_pos()

        for i, (key, name) in enumerate(self.options):
            y = start_y + i * (btn_height + spacing)
            row_rect = pygame.Rect(panel_x + 40, y, btn_width, btn_height)

            is_hovered = row_rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_index)

            if is_hovered:
                self.selected_index = i

            # Фон строки
            if is_selected or is_hovered:
                pygame.draw.rect(surface, (60, 70, 90), row_rect, border_radius=6)
                pygame.draw.rect(surface, GOLD, row_rect, 2, border_radius=6)
            else:
                pygame.draw.rect(surface, (45, 55, 75), row_rect, border_radius=6)
                pygame.draw.rect(surface, (80, 90, 110), row_rect, 1, border_radius=6)

            # Название
            name_surf = font.render(name, True, WHITE)
            surface.blit(name_surf, (panel_x + 55, y + (btn_height - name_surf.get_height()) // 2))

            # Значение
            value = self._get_value_text(key)
            value_surf = font.render(value, True, GOLD)
            value_x = panel_x + btn_width - value_surf.get_width() + 20
            surface.blit(value_surf, (value_x, y + (btn_height - value_surf.get_height()) // 2))

            # Стрелки
            if is_selected or is_hovered:
                arrow_font = pygame.font.SysFont("Arial", int(18 * scale), bold=True)
                left = arrow_font.render("◀", True, GOLD)
                right = arrow_font.render("▶", True, GOLD)
                surface.blit(left, (value_x - 25, y + (btn_height - left.get_height()) // 2))
                surface.blit(right, (panel_x + btn_width + 25, y + (btn_height - right.get_height()) // 2))

        # Кнопки действий
        action_btn_width = int(180 * scale)
        action_btn_height = int(45 * scale)
        action_y = panel_y + panel_height - int(70 * scale)

        # Применить
        apply_rect = pygame.Rect(panel_x + panel_width // 2 - action_btn_width - 15,
                                 action_y, action_btn_width, action_btn_height)
        apply_hovered = apply_rect.collidepoint(mouse_pos)
        apply_btn = Button(apply_rect.x, apply_rect.y, action_btn_width, action_btn_height,
                           "✓ Применить", color=(50, 150, 50), font_size=int(18 * scale))
        apply_btn.is_hovered = apply_hovered
        apply_btn.draw(surface)

        # Назад
        back_rect = pygame.Rect(panel_x + panel_width // 2 + 15,
                                action_y, action_btn_width, action_btn_height)
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_btn = Button(back_rect.x, back_rect.y, action_btn_width, action_btn_height,
                          "← Назад", color=(150, 80, 50), font_size=int(18 * scale))
        back_btn.is_hovered = back_hovered
        back_btn.draw(surface)

        # Подсказка
        hint_font = pygame.font.SysFont("Arial", int(12 * scale))
        hint = "↑↓ Выбор | ←→ Изменить | ЛКМ/ПКМ Клик | Enter Переключить"
        hint_surf = hint_font.render(hint, True, LIGHT_GRAY)
        surface.blit(hint_surf, hint_surf.get_rect(centerx=panel_x + panel_width // 2,
                                                   y=panel_y + panel_height - 25))


class MainMenu:
    def __init__(self):
        self.options = ["Новая игра", "Продолжить", "Настройки", "Выход"]
        self.selected_index = 0

    def handle_input(self, event, screen_size):
        screen_w, screen_h = screen_size
        scale = min(screen_w / 1024, screen_h / 768)

        btn_width = int(280 * scale)
        btn_height = int(55 * scale)
        btn_spacing = int(15 * scale)
        start_y = int(screen_h * 0.45)

        # Клик мыши
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i in range(len(self.options)):
                btn_y = start_y + i * (btn_height + btn_spacing)
                btn_rect = pygame.Rect((screen_w - btn_width) // 2, btn_y, btn_width, btn_height)
                if btn_rect.collidepoint(mouse_pos):
                    return self.options[i]

        # Клавиатура
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected_index]

        return None

    def draw(self, surface):
        screen_w = surface.get_width()
        screen_h = surface.get_height()

        # Градиентный фон
        for y in range(screen_h):
            ratio = y / screen_h
            r = int(20 + 30 * ratio)
            g = int(20 + 40 * ratio)
            b = int(60 + 40 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (screen_w, y))

        # Звёзды
        import random
        random.seed(42)
        for _ in range(200):
            x = random.randint(0, screen_w)
            y = random.randint(0, screen_h // 2)
            brightness = random.randint(100, 255)
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), random.randint(1, 2))

        scale = min(screen_w / 1024, screen_h / 768)

        # Заголовок
        title_font = pygame.font.SysFont("Arial", int(72 * scale), bold=True)
        shadow = title_font.render("RPG ADVENTURE", True, (40, 30, 10))
        title = title_font.render("RPG ADVENTURE", True, GOLD)
        title_rect = title.get_rect(centerx=screen_w // 2, y=int(screen_h * 0.15))
        surface.blit(shadow, title_rect.move(4, 4))
        surface.blit(title, title_rect)

        # Подзаголовок
        sub_font = pygame.font.SysFont("Arial", int(24 * scale))
        subtitle = sub_font.render("Индивидуальный проект", True, WHITE)
        surface.blit(subtitle, subtitle.get_rect(centerx=screen_w // 2, y=title_rect.bottom + 20))

        # Кнопки
        btn_width = int(280 * scale)
        btn_height = int(55 * scale)
        btn_spacing = int(15 * scale)
        start_y = int(screen_h * 0.45)

        colors = [(50, 120, 200), (50, 150, 100), (120, 100, 150), (150, 70, 70)]
        mouse_pos = pygame.mouse.get_pos()

        for i, (option, color) in enumerate(zip(self.options, colors)):
            btn_y = start_y + i * (btn_height + btn_spacing)
            btn_rect = pygame.Rect((screen_w - btn_width) // 2, btn_y, btn_width, btn_height)

            is_hovered = btn_rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_index)

            if is_hovered:
                self.selected_index = i

            btn = Button(btn_rect.x, btn_rect.y, btn_width, btn_height, option,
                         color=color, font_size=int(22 * scale))
            btn.is_hovered = is_hovered
            btn.is_selected = is_selected
            btn.draw(surface)

        # Управление
        ctrl_font = pygame.font.SysFont("Arial", int(14 * scale))
        controls = [
            "WASD / Стрелки — Движение  |  E — Взаимодействие",
            "I — Инвентарь  |  Q — Квесты  |  F11 — Полный экран",
        ]

        ctrl_y = screen_h - len(controls) * int(22 * scale) - int(30 * scale)
        for i, ctrl in enumerate(controls):
            surf = ctrl_font.render(ctrl, True, LIGHT_GRAY)
            surface.blit(surf, surf.get_rect(centerx=screen_w // 2, y=ctrl_y + i * int(22 * scale)))