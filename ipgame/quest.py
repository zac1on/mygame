# quest.py
import pygame
from settings import *
from button import Panel


class Quest:
    def __init__(self, quest_id, title, description, quest_type, target, required_count, rewards):
        self.id = quest_id
        self.title = title
        self.description = description
        self.quest_type = quest_type
        self.target = target
        self.required_count = required_count
        self.current_count = 0
        self.completed = False
        self.turned_in = False
        self.rewards = rewards

    def update_progress(self, target, count=1):
        if self.turned_in:
            return False
        if self.quest_type == "kill" and target == self.target:
            self.current_count += count
            if self.current_count >= self.required_count:
                self.completed = True
            return True
        return False

    def check_completion(self, inventory):
        if self.turned_in:
            return False
        if self.quest_type == "collect":
            item_count = inventory.count_item(self.target)
            self.current_count = min(item_count, self.required_count)
            if item_count >= self.required_count:
                self.completed = True
                return True
        return self.completed

    def turn_in(self, player, inventory):
        if not self.completed or self.turned_in:
            return False

        if self.quest_type == "collect":
            if not inventory.has_item(self.target, self.required_count):
                return False
            inventory.remove_item(self.target, self.required_count)

        self.turned_in = True

        if "exp" in self.rewards:
            player.gain_exp(self.rewards["exp"])
        if "gold" in self.rewards:
            player.gold += self.rewards["gold"]
        if "item" in self.rewards:
            inventory.add_item(self.rewards["item"])

        return True


class QuestManager:
    def __init__(self):
        self.quests = {}
        self.active_quests = []
        self._init_quests()

    def _init_quests(self):
        self.quests["kill_slimes"] = Quest(
            "kill_slimes", "Охота на слизней",
            "Убейте 3 слизней", "kill", "slime", 3,
            {"exp": 60, "gold": 30, "item": "health_potion"}
        )
        self.quests["bring_ore"] = Quest(
            "bring_ore", "Руда для кузнеца",
            "Принесите 2 куска руды", "collect", "ore", 2,
            {"exp": 80, "gold": 50, "item": "iron_sword"}
        )

    def accept_quest(self, quest_id):
        if quest_id in self.quests and quest_id not in self.active_quests:
            if not self.quests[quest_id].turned_in:
                self.active_quests.append(quest_id)
                return True
        return False

    def notify_kill(self, enemy_type):
        for qid in self.active_quests:
            if self.quests[qid].quest_type == "kill":
                self.quests[qid].update_progress(enemy_type)

    def check_collect_quests(self, inventory):
        for qid in self.active_quests:
            if self.quests[qid].quest_type == "collect":
                self.quests[qid].check_completion(inventory)

    def notify_collect(self, item_type):
        pass

    def get_quest(self, quest_id):
        return self.quests.get(quest_id)

    def get_active_quests(self):
        return [self.quests[qid] for qid in self.active_quests]


class QuestLogUI:
    def __init__(self):
        self.visible = False

    def toggle(self):
        self.visible = not self.visible

    def draw(self, surface, quest_manager, inventory=None):
        if not self.visible:
            return

        screen_w = surface.get_width()
        screen_h = surface.get_height()

        scale = min(screen_w / 1024, screen_h / 768)
        scale = max(0.7, min(scale, 1.3))

        # Панель
        width = int(500 * scale)
        height = int(400 * scale)
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        # Затемнение
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel = Panel(x, y, width, height, bg_color=(30, 40, 55))
        panel.draw(surface, "📜 КВЕСТЫ")

        # Квесты
        font = pygame.font.SysFont("Arial", int(18 * scale), bold=True)
        small_font = pygame.font.SysFont("Arial", int(14 * scale))

        quest_y = y + int(60 * scale)
        active = quest_manager.get_active_quests()

        if not active:
            empty = small_font.render("Нет активных квестов", True, LIGHT_GRAY)
            surface.blit(empty, (x + 25, quest_y))
        else:
            for quest in active:
                # Статус
                if quest.turned_in:
                    icon, status, color = "✅", "Завершён", GREEN
                elif quest.completed:
                    icon, status, color = "⭐", "Сдайте NPC!", YELLOW
                else:
                    icon, status, color = "📋", f"{quest.current_count}/{quest.required_count}", WHITE

                # Название
                title = font.render(f"{icon} {quest.title}", True, color)
                surface.blit(title, (x + 25, quest_y))
                quest_y += int(25 * scale)

                # Описание
                desc = small_font.render(quest.description, True, LIGHT_GRAY)
                surface.blit(desc, (x + 40, quest_y))
                quest_y += int(22 * scale)

                # Прогресс бар
                bar_width = int(200 * scale)
                bar_height = int(12 * scale)
                progress = quest.current_count / quest.required_count if quest.required_count > 0 else 0

                pygame.draw.rect(surface, (50, 50, 60), (x + 40, quest_y, bar_width, bar_height), border_radius=4)
                if progress > 0:
                    fill_color = GREEN if quest.completed else (80, 140, 200)
                    pygame.draw.rect(surface, fill_color,
                                     (x + 40, quest_y, int(bar_width * progress), bar_height), border_radius=4)
                pygame.draw.rect(surface, WHITE, (x + 40, quest_y, bar_width, bar_height), 1, border_radius=4)

                # Текст прогресса
                prog_text = small_font.render(status, True, color)
                surface.blit(prog_text, (x + 50 + bar_width, quest_y))
                quest_y += int(20 * scale)

                # Награды
                rewards = []
                if "exp" in quest.rewards:
                    rewards.append(f"+{quest.rewards['exp']} EXP")
                if "gold" in quest.rewards:
                    rewards.append(f"+{quest.rewards['gold']} G")
                if "item" in quest.rewards:
                    item = ITEMS.get(quest.rewards["item"], {})
                    rewards.append(item.get("name", "Предмет"))

                reward_text = small_font.render(f"🎁 {', '.join(rewards)}", True, GOLD)
                surface.blit(reward_text, (x + 40, quest_y))
                quest_y += int(35 * scale)

                # Разделитель
                pygame.draw.line(surface, (60, 70, 90), (x + 25, quest_y), (x + width - 25, quest_y))
                quest_y += int(15 * scale)

        # Подсказка
        hint = small_font.render("Нажмите Q для закрытия", True, LIGHT_GRAY)
        surface.blit(hint, hint.get_rect(centerx=x + width // 2, y=y + height - 30))