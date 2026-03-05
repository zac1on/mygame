import pygame
from settings import *
from bullet import Bullet
from sounds import sound_manager

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        
        # Создаем простой спрайт (треугольник)
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 40), (50, 40)])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 20
        
        self.speedx = 0
        self.health = PLAYER_HEALTH
        self.shoot_delay = 250  # миллисекунды
        self.last_shot = pygame.time.get_ticks()
        self.power_level = 1  # Уровень оружия

    def update(self):
        """Обновление игрока"""
        self.speedx = 0
        
        # Управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speedx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speedx = PLAYER_SPEED
        if keys[pygame.K_SPACE]:
            self.shoot()
        
        # Движение
        self.rect.x += self.speedx
        
        # Границы экрана
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        """Стрельба"""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            sound_manager.play('shoot')
            
            if self.power_level == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                self.game.all_sprites.add(bullet)
                self.game.bullets.add(bullet)
            
            elif self.power_level >= 2:
                # Тройной выстрел
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.centerx, self.rect.top)
                bullet3 = Bullet(self.rect.right, self.rect.centery)
                
                self.game.all_sprites.add(bullet1, bullet2, bullet3)
                self.game.bullets.add(bullet1, bullet2, bullet3)

    def power_up(self):
        """Улучшить оружие"""
        self.power_level += 1
        if self.power_level > 2:
            self.power_level = 2

    def heal(self):
        """Восстановить здоровье"""
        self.health += 30
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH