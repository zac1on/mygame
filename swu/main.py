import pygame
import random
import sys
from settings import *
from player import Player
from enemy import Enemy
from bullet import Bullet
from powerup import PowerUp
from sounds import sound_manager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "menu"  # menu, playing, game_over


        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()


        self.player = Player(self)
        self.all_sprites.add(self.player)


        self.score = 0
        self.enemy_timer = 0
        self.powerup_timer = 0
        self.high_score = self.load_high_score()
        self.difficulty = 1


        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def load_high_score(self):
        try:
            with open('data/highscore.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open('data/highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def new_game(self):

        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.powerups.empty()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.score = 0
        self.difficulty = 1
        self.game_state = "playing"

    def spawn_enemy(self):
        enemy = Enemy(self)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)

    def spawn_powerup(self):

        powerup = PowerUp(self)
        self.all_sprites.add(powerup)
        self.powerups.add(powerup)

    def update(self):
        """Обновление игры"""
        if self.game_state != "playing":
            return

        # Обновить все спрайты
        self.all_sprites.update()

        # Спавн врагов (быстрее с сложностью)
        self.enemy_timer += 1
        spawn_rate = max(20, ENEMY_SPAWN_RATE - self.difficulty * 5)
        if self.enemy_timer >= spawn_rate:
            self.spawn_enemy()
            self.enemy_timer = 0

        # Спавн бонусов
        self.powerup_timer += 1
        if self.powerup_timer >= POWERUP_SPAWN_RATE:
            self.spawn_powerup()
            self.powerup_timer = 0

        # Проверка попаданий пуль по врагам
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += 10
            sound_manager.play('explosion')
            
            # Усложнение: каждые 50 очков
            if self.score % 50 == 0:
                self.difficulty += 1

        # Проверка столкновений игрока с врагами
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.health -= 20
            sound_manager.play('player_hit')
            if self.player.health <= 0:
                sound_manager.play('game_over')
                self.game_state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()

        # Проверка столкновений игрока с бонусами
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for hit in hits:
            hit.apply(self.player)
            sound_manager.play('powerup')

    def draw(self):
        """Отрисовка"""
        self.screen.fill(BLACK)

        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        """Главное меню"""
        title = self.big_font.render("SPACE SHOOTER", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH / 2, HEIGHT / 3))
        self.screen.blit(title, title_rect)

        prompt = self.font.render("Press SPACE to Start", True, GREEN)
        prompt_rect = prompt.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.screen.blit(prompt, prompt_rect)

        high_score_text = self.font.render(f"High Score: {self.high_score}", True, YELLOW)
        high_score_rect = high_score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 60))
        self.screen.blit(high_score_text, high_score_rect)

    def draw_game(self):
        """Игровой экран"""
        self.all_sprites.draw(self.screen)

        # Счёт
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Здоровье
        health_text = self.font.render(f"Health: {self.player.health}", True, GREEN)
        self.screen.blit(health_text, (10, 50))

        # Полоска здоровья
        health_bar_width = 200
        health_bar_height = 20
        fill = (self.player.health / PLAYER_HEALTH) * health_bar_width

        pygame.draw.rect(self.screen, RED, (10, 90, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, GREEN, (10, 90, fill, health_bar_height))
        pygame.draw.rect(self.screen, WHITE, (10, 90, health_bar_width, health_bar_height), 2)

    def draw_game_over(self):
        """Экран Game Over"""
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH / 2, HEIGHT / 3))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.font.render(f"Your Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.screen.blit(score_text, score_rect)

        if self.score >= self.high_score:
            new_record = self.font.render("NEW RECORD!", True, YELLOW)
            new_record_rect = new_record.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
            self.screen.blit(new_record, new_record_rect)

        restart = self.font.render("Press SPACE to Restart", True, GREEN)
        restart_rect = restart.get_rect(center=(WIDTH / 2, HEIGHT - 100))
        self.screen.blit(restart, restart_rect)

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == "menu" or self.game_state == "game_over":
                        self.new_game()

                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def run(self):
        """Главный игровой цикл"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()