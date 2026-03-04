# main.py
import pygame
import sys
import json
import math
import os
from settings import *
from player import Player
from enemy import Enemy
from npc import NPC
from map_manager import MapManager
from camera import Camera
from inventory import Inventory, InventoryUI
from ui import UI, PauseMenu, SettingsMenu, MainMenu
from combat import CombatSystem
from quest import QuestManager, QuestLogUI


class Game:
    def __init__(self):
        pygame.init()

        self.game_settings = GAME_SETTINGS
        self._apply_display_settings()

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.main_menu = MainMenu()
        self.settings_menu = SettingsMenu(self.game_settings)

        self._init_game_objects()

    def _apply_display_settings(self):
        """Применить настройки отображения"""
        if self.game_settings.fullscreen:
            # Полноэкранный режим - используем нативное разрешение монитора
            self.screen = pygame.display.set_mode(
                (self.game_settings.native_width, self.game_settings.native_height),
                pygame.FULLSCREEN
            )
            self.screen_width = self.game_settings.native_width
            self.screen_height = self.game_settings.native_height
        else:
            # Оконный режим
            self.screen_width, self.screen_height = self.game_settings.get_resolution()
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.RESIZABLE
            )

        # Обновляем камеру если она существует
        if hasattr(self, 'camera'):
            self.camera.update_screen_size(self.screen_width, self.screen_height)

    def _init_game_objects(self):
        """Инициализация игровых объектов"""
        self.map_manager = MapManager()
        self.camera = Camera(self.map_manager.map_width, self.map_manager.map_height)

        # Обновляем размер экрана в камере
        self.camera.update_screen_size(self.screen_width, self.screen_height)

        self.player = Player(5, 1)

        self.enemies = []
        for ex, ey, etype in ENEMY_DATA:
            self.enemies.append(Enemy(ex, ey, etype))

        self.npcs = []
        for nx, ny, name, dialogues, quest_id in NPC_DATA:
            self.npcs.append(NPC(nx, ny, name, dialogues, quest_id))

        self.world_items = []
        for ix, iy, item_key in ITEM_SPAWNS:
            rect = pygame.Rect(ix * TILE_SIZE + 16, iy * TILE_SIZE + 16, 32, 32)
            self.world_items.append({"rect": rect, "key": item_key, "collected": False})

        self.item_sprites = {}
        self._load_item_sprites()

        self.inventory = Inventory()
        self.inventory_ui = InventoryUI()
        self.ui = UI()
        self.ui.init_fonts()
        self.pause_menu = PauseMenu()
        self.combat = CombatSystem()
        self.quest_manager = QuestManager()
        self.quest_log_ui = QuestLogUI()

        self.in_dialogue = False
        self.dialogue_npc = None
        self.dialogue_page = 0

        self.inventory.add_item("health_potion", 2)

    def _load_item_sprites(self):
        item_size = 32
        for item_key in ITEMS.keys():
            paths = [f"assets/items/{item_key}.png", f"assets/{item_key}.png"]
            for path in paths:
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        self.item_sprites[item_key] = pygame.transform.scale(sprite, (item_size, item_size))
                        break
                    except:
                        pass

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        self.game_settings.fullscreen = not self.game_settings.fullscreen
        self._apply_display_settings()
        self.game_settings.save()
        self.ui.init_fonts()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Изменение размера окна
            if event.type == pygame.VIDEORESIZE:
                if not self.game_settings.fullscreen:
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                    self.camera.update_screen_size(self.screen_width, self.screen_height)

            # F11 - полноэкранный режим
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue

            # Передаём ВСЕ события в соответствующие обработчики
            if self.state == "menu":
                self._handle_menu_events(event)
            elif self.state == "playing":
                self._handle_game_events(event)
            elif self.state == "game_over":
                self._handle_gameover_events(event)

    def _handle_menu_events(self, event):
        screen_size = (self.screen.get_width(), self.screen.get_height())

        # Настройки поверх главного меню
        if self.settings_menu.visible:
            result = self.settings_menu.handle_input(event, screen_size)
            if result == "apply":
                self._apply_display_settings()
                self.settings_menu.visible = False
            return

        # Главное меню
        result = self.main_menu.handle_input(event, screen_size)

        if result == "Новая игра":
            self._init_game_objects()
            self.state = "playing"
        elif result == "Продолжить":
            if os.path.exists("savegame.json"):
                self._init_game_objects()
                self.load_game()
            self.state = "playing"
        elif result == "Настройки":
            self.settings_menu.toggle()
        elif result == "Выход":
            self.running = False

    def _handle_game_events(self, event):
        screen_size = (self.screen.get_width(), self.screen.get_height())

        # Бой - передаём ВСЕ события
        if self.combat.in_combat:
            self.combat.handle_input(event, self.player)
            return

        # Настройки
        if self.settings_menu.visible:
            result = self.settings_menu.handle_input(event, screen_size)
            if result == "apply":
                self._apply_display_settings()
                self.settings_menu.visible = False
                self.pause_menu.visible = False
            return

        # Пауза - передаём ВСЕ события
        if self.pause_menu.visible:
            result = self.pause_menu.handle_input(event, screen_size)
            if result == "Продолжить":
                self.pause_menu.toggle()
            elif result == "Настройки":
                self.settings_menu.toggle()
            elif result == "Сохранить":
                self.save_game()
                self.ui.show_message("Игра сохранена!")
                self.pause_menu.toggle()
            elif result == "Выйти":
                self.state = "menu"
                self.pause_menu.toggle()
            return

        # Остальные события только для KEYDOWN
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.pause_menu.toggle()
            return

        # Инвентарь
        if self.inventory_ui.visible:
            result = self.inventory_ui.handle_input(event, self.inventory, self.player)
            if result:
                self.ui.show_message(result)
            if event.key == pygame.K_i:
                self.inventory_ui.toggle()
            return

        if event.key == pygame.K_i:
            self.inventory_ui.toggle()
            return

        if event.key == pygame.K_q:
            self.quest_log_ui.toggle()
            return

        if self.quest_log_ui.visible:
            return

        # Диалог
        if self.in_dialogue:
            if event.key in (pygame.K_e, pygame.K_RETURN):
                self.dialogue_page += 1
                if self.dialogue_page >= len(self.dialogue_npc.dialogues):
                    self.in_dialogue = False
                    if self.dialogue_npc.quest_id:
                        quest = self.quest_manager.get_quest(self.dialogue_npc.quest_id)
                        if quest and not quest.turned_in:
                            if quest.completed:
                                if quest.turn_in(self.player, self.inventory):
                                    self.ui.show_message(f"Квест '{quest.title}' завершён!", 180)
                            elif self.dialogue_npc.quest_id not in self.quest_manager.active_quests:
                                self.quest_manager.accept_quest(self.dialogue_npc.quest_id)
                                self.ui.show_message(f"Новый квест: {quest.title}", 120)
            return

        if event.key == pygame.K_e:
            self._interact()

        if event.key == pygame.K_F5:
            self.save_game()
            self.ui.show_message("Игра сохранена!")
        elif event.key == pygame.K_F9:
            self.load_game()
            self.ui.show_message("Игра загружена!")

    def _handle_menu_events(self, event):
        if self.settings_menu.visible:
            result = self.settings_menu.handle_input(event)
            if result == "apply":
                self._apply_display_settings()
                self.settings_menu.visible = False
            elif result == "back":
                pass
            return

        result = self.main_menu.handle_input(event)

        if result == "Новая игра":
            self._init_game_objects()
            self.state = "playing"
        elif result == "Продолжить":
            if os.path.exists("savegame.json"):
                self._init_game_objects()
                self.load_game()
            self.state = "playing"
        elif result == "Настройки":
            self.settings_menu.toggle()
        elif result == "Выход":
            self.running = False

    def _handle_gameover_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._init_game_objects()
                self.state = "playing"
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"

    def _handle_game_events(self, event):
        if self.combat.in_combat:
            self.combat.handle_input(event, self.player)
            return

        if self.settings_menu.visible:
            result = self.settings_menu.handle_input(event)
            if result == "apply":
                self._apply_display_settings()
                self.settings_menu.visible = False
                self.pause_menu.visible = False
            return

        if event.type != pygame.KEYDOWN:
            return

        if self.pause_menu.visible:
            result = self.pause_menu.handle_input(event)
            if result == "Продолжить":
                self.pause_menu.toggle()
            elif result == "Настройки":
                self.settings_menu.toggle()
            elif result == "Сохранить":
                self.save_game()
                self.ui.show_message("Игра сохранена!")
                self.pause_menu.toggle()
            elif result == "Выйти":
                self.state = "menu"
                self.pause_menu.toggle()
            return

        if event.key == pygame.K_ESCAPE:
            self.pause_menu.toggle()
            return

        if self.inventory_ui.visible:
            result = self.inventory_ui.handle_input(event, self.inventory, self.player)
            if result:
                self.ui.show_message(result)
            if event.key == pygame.K_i:
                self.inventory_ui.toggle()
            return

        if event.key == pygame.K_i:
            self.inventory_ui.toggle()
            return

        if event.key == pygame.K_q:
            self.quest_log_ui.toggle()
            return

        if self.quest_log_ui.visible:
            return

        if self.in_dialogue:
            if event.key == pygame.K_e or event.key == pygame.K_RETURN:
                self.dialogue_page += 1
                if self.dialogue_page >= len(self.dialogue_npc.dialogues):
                    self.in_dialogue = False
                    if self.dialogue_npc.quest_id:
                        quest = self.quest_manager.get_quest(self.dialogue_npc.quest_id)
                        if quest and not quest.turned_in:
                            if quest.completed:
                                if quest.turn_in(self.player, self.inventory):
                                    self.ui.show_message(f"Квест '{quest.title}' завершён!", 180)
                            elif self.dialogue_npc.quest_id not in self.quest_manager.active_quests:
                                self.quest_manager.accept_quest(self.dialogue_npc.quest_id)
                                self.ui.show_message(f"Новый квест: {quest.title}", 120)
            return

        if event.key == pygame.K_e:
            self._interact()

        if event.key == pygame.K_F5:
            self.save_game()
            self.ui.show_message("Игра сохранена!")
        elif event.key == pygame.K_F9:
            self.load_game()
            self.ui.show_message("Игра загружена!")

    def _interact(self):
        for npc in self.npcs:
            if npc.can_interact(self.player.rect):
                self.in_dialogue = True
                self.dialogue_npc = npc
                self.dialogue_page = 0
                return

        for item in self.world_items:
            if not item["collected"]:
                dist = math.hypot(
                    self.player.rect.centerx - item["rect"].centerx,
                    self.player.rect.centery - item["rect"].centery)
                if dist < 60:
                    if self.inventory.add_item(item["key"]):
                        item["collected"] = True
                        self.ui.show_message(f"Получено: {ITEMS[item['key']]['name']}")
                        self.quest_manager.notify_collect(item["key"])
                    else:
                        self.ui.show_message("Инвентарь полон!")
                    return

    def update(self):
        if self.state != "playing":
            return

        if (self.combat.in_combat or self.pause_menu.visible or
                self.inventory_ui.visible or self.in_dialogue or
                self.quest_log_ui.visible or self.settings_menu.visible):
            if self.combat.in_combat:
                self.combat.update(self.player)
                if self.player.hp <= 0:
                    self.state = "game_over"
            self.ui.update()
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1

        self.player.move(dx, dy, self.map_manager.walls)
        self.camera.update(self.player.rect)

        for enemy in self.enemies:
            enemy.update(self.player.rect, self.map_manager.walls)
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                self.combat.start_combat(enemy)
                break

        for enemy in self.enemies:
            if not enemy.alive and enemy.respawn_timer == enemy.respawn_time - 1:
                self.quest_manager.notify_kill(enemy.type)

        self.quest_manager.check_collect_quests(self.inventory)
        self.ui.update()

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "menu":
            self._draw_menu()
        elif self.state == "playing":
            self._draw_game()
        elif self.state == "game_over":
            self._draw_game_over()

        if self.game_settings.show_fps:
            fps_font = pygame.font.SysFont("Arial", 16)
            fps_text = fps_font.render(f"FPS: {int(self.clock.get_fps())}", True, GREEN)
            self.screen.blit(fps_text, (10, self.screen.get_height() - 25))

        pygame.display.flip()

    def _draw_menu(self):
        self.main_menu.draw(self.screen)
        if self.settings_menu.visible:
            self.settings_menu.draw(self.screen)

    def _draw_game(self):
        self.map_manager.draw(self.screen, self.camera)
        self._draw_world_items()

        for npc in self.npcs:
            npc.draw(self.screen, self.camera, self.player.rect)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        self.player.draw(self.screen, self.camera)

        if self.game_settings.show_minimap:
            self._draw_minimap()

        self.ui.draw_hud(self.screen, self.player)
        self.ui.draw_message(self.screen)

        if self.in_dialogue and self.dialogue_npc:
            page = min(self.dialogue_page, len(self.dialogue_npc.dialogues) - 1)
            self.ui.draw_dialogue(self.screen, self.dialogue_npc.name,
                                  self.dialogue_npc.dialogues[page], page,
                                  len(self.dialogue_npc.dialogues))

        self.combat.draw(self.screen, self.player)
        self.inventory_ui.draw(self.screen, self.inventory, self.player)
        self.quest_log_ui.draw(self.screen, self.quest_manager, self.inventory)
        self.pause_menu.draw(self.screen)

        if self.settings_menu.visible:
            self.settings_menu.draw(self.screen)

    def _draw_world_items(self):
        for item in self.world_items:
            if not item["collected"]:
                draw_rect = self.camera.apply(item["rect"])

                # Проверяем видимость на экране
                if (draw_rect.right < 0 or draw_rect.left > self.screen_width or
                        draw_rect.bottom < 0 or draw_rect.top > self.screen_height):
                    continue

                item_key = item["key"]
                item_data = ITEMS[item_key]

                t = pygame.time.get_ticks() / 1000
                offset_y = int(math.sin(t * 3 + item["rect"].x * 0.1) * 4)
                float_rect = draw_rect.move(0, offset_y)

                glow_surf = pygame.Surface((44, 44), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*item_data["color"], 60), (22, 22), 22)
                self.screen.blit(glow_surf, (float_rect.x - 6, float_rect.y - 6))

                if item_key in self.item_sprites:
                    self.screen.blit(self.item_sprites[item_key], float_rect)
                else:
                    self._draw_item_default(float_rect, item_key, item_data)

    def _draw_item_default(self, rect, item_key, item_data):
        cx, cy = rect.centerx, rect.centery
        color = item_data["color"]
        if "potion" in item_key:
            self._draw_potion(cx, cy, color)
        elif "sword" in item_key:
            self._draw_sword(cx, cy, color)
        elif "armor" in item_key:
            self._draw_armor(cx, cy, color)
        elif item_key == "ore":
            self._draw_ore(cx, cy, color)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=6)

    def _draw_potion(self, cx, cy, color):
        bottle = pygame.Rect(cx - 8, cy - 4, 16, 16)
        pygame.draw.rect(self.screen, color, bottle, border_radius=5)
        pygame.draw.rect(self.screen, (180, 180, 180), (cx - 4, cy - 10, 8, 6))
        pygame.draw.rect(self.screen, (139, 90, 43), (cx - 3, cy - 13, 6, 4))
        pygame.draw.line(self.screen, WHITE, (cx - 4, cy - 2), (cx - 4, cy + 6), 2)

    def _draw_sword(self, cx, cy, color):
        pygame.draw.line(self.screen, color, (cx - 10, cy + 10), (cx + 8, cy - 10), 4)
        pygame.draw.line(self.screen, GOLD, (cx - 5, cy + 1), (cx + 3, cy + 5), 4)
        pygame.draw.line(self.screen, (100, 60, 20), (cx - 10, cy + 10), (cx - 13, cy + 13), 5)

    def _draw_armor(self, cx, cy, color):
        points = [(cx, cy - 10), (cx + 11, cy - 5), (cx + 9, cy + 10),
                  (cx, cy + 12), (cx - 9, cy + 10), (cx - 11, cy - 5)]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, WHITE, points, 2)

    def _draw_ore(self, cx, cy, color):
        points = [(cx - 10, cy + 7), (cx - 7, cy - 5), (cx + 3, cy - 9),
                  (cx + 10, cy - 3), (cx + 7, cy + 9), (cx - 3, cy + 9)]
        pygame.draw.polygon(self.screen, (90, 90, 90), points)
        pygame.draw.line(self.screen, color, (cx - 5, cy), (cx + 4, cy - 3), 3)

    def _draw_minimap(self):
        """Адаптивная миникарта"""
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        scale = min(screen_w / 1024, screen_h / 768)
        scale = max(0.6, min(scale, 1.2))

        mm_scale = int(4 * scale)
        mm_width = len(GAME_MAP[0]) * mm_scale
        mm_height = len(GAME_MAP) * mm_scale
        mm_x = screen_w - mm_width - int(15 * scale)
        mm_y = int(15 * scale)

        # Панель миникарты
        panel_rect = pygame.Rect(mm_x - 5, mm_y - 5, mm_width + 10, mm_height + 10)
        pygame.draw.rect(self.screen, (20, 25, 40), panel_rect, border_radius=6)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 2, border_radius=6)

        # Тайлы
        for row in range(len(GAME_MAP)):
            for col in range(len(GAME_MAP[row])):
                tile = GAME_MAP[row][col]
                tx = mm_x + col * mm_scale
                ty = mm_y + row * mm_scale

                colors = {0: DARK_GREEN, 1: (80, 70, 60), 2: BLUE, 3: (140, 120, 80), 4: DARK_GREEN}
                color = colors.get(tile, DARK_GREEN)
                pygame.draw.rect(self.screen, color, (tx, ty, mm_scale, mm_scale))

        # Маркеры
        marker_size = max(2, int(3 * scale))

        for enemy in self.enemies:
            if enemy.alive:
                ex = mm_x + int(enemy.rect.centerx / TILE_SIZE * mm_scale)
                ey = mm_y + int(enemy.rect.centery / TILE_SIZE * mm_scale)
                pygame.draw.rect(self.screen, RED, (ex, ey, marker_size, marker_size))

        for npc in self.npcs:
            nx = mm_x + int(npc.rect.centerx / TILE_SIZE * mm_scale)
            ny = mm_y + int(npc.rect.centery / TILE_SIZE * mm_scale)
            pygame.draw.rect(self.screen, YELLOW, (nx, ny, marker_size, marker_size))

        px = mm_x + int(self.player.rect.centerx / TILE_SIZE * mm_scale)
        py = mm_y + int(self.player.rect.centery / TILE_SIZE * mm_scale)
        pygame.draw.rect(self.screen, WHITE, (px - 1, py - 1, marker_size + 2, marker_size + 2))

    def _draw_game_over(self):
        self.screen.fill((20, 0, 0))
        font = pygame.font.SysFont("Arial", 64, bold=True)
        title = font.render("ВЫ ПОГИБЛИ", True, RED)
        self.screen.blit(title, title.get_rect(centerx=self.screen.get_width() // 2,
                                               centery=self.screen.get_height() // 3))
        sub_font = pygame.font.SysFont("Arial", 24)
        texts = [f"Уровень: {self.player.level}", f"Золото: {self.player.gold}", "",
                 "ENTER - перезапуск", "ESC - меню"]
        for i, t in enumerate(texts):
            surf = sub_font.render(t, True, WHITE if i < 2 else YELLOW)
            self.screen.blit(surf, surf.get_rect(centerx=self.screen.get_width() // 2,
                                                 y=self.screen.get_height() // 2 + i * 35))

    def save_game(self):
        data = {
            "player": {
                "x": self.player.rect.x, "y": self.player.rect.y,
                "hp": self.player.hp, "mana": self.player.mana,
                "level": self.player.level, "exp": self.player.exp,
                "gold": self.player.gold, "base_attack": self.player.base_attack,
                "base_defense": self.player.base_defense, "max_hp": self.player.max_hp,
                "max_mana": self.player.max_mana, "exp_to_next": self.player.exp_to_next,
                "weapon": self.player.weapon, "armor": self.player.armor,
            },
            "inventory": self.inventory.items,
            "quests": {qid: {"current_count": q.current_count, "completed": q.completed,
                             "turned_in": q.turned_in} for qid, q in self.quest_manager.quests.items()},
            "active_quests": self.quest_manager.active_quests,
            "collected_items": [i for i, item in enumerate(self.world_items) if item["collected"]],
        }
        with open("savegame.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_game(self):
        try:
            with open("savegame.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            p = data["player"]
            for k, v in p.items():
                if k == "x":
                    self.player.rect.x = v
                elif k == "y":
                    self.player.rect.y = v
                else:
                    setattr(self.player, k, v)
            self.inventory.items = data["inventory"]
            for qid, qdata in data["quests"].items():
                if qid in self.quest_manager.quests:
                    q = self.quest_manager.quests[qid]
                    q.current_count = qdata["current_count"]
                    q.completed = qdata["completed"]
                    q.turned_in = qdata["turned_in"]
            self.quest_manager.active_quests = data["active_quests"]
            for i in data["collected_items"]:
                if i < len(self.world_items):
                    self.world_items[i]["collected"] = True
        except:
            pass


if __name__ == "__main__":
    game = Game()
    game.run()