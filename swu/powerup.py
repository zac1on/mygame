import pygame
import random
from settings import *


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.type = random.choice(['health', 'power'])
        
        self.image = pygame.Surface((20, 20))
        if self.type == 'health':
            self.image.fill(GREEN)
        else:
            self.image.fill(BLUE)
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = POWERUP_SPEED

    def update(self):
        """Движение бонуса"""
        self.rect.y += self.speed
        
        # Удалить бонус, если он вышел за экран
        if self.rect.top > HEIGHT + 10:
            self.kill()

    def apply(self, player):
        """Применить эффект бонуса"""
        if self.type == 'health':
            player.heal()
        elif self.type == 'power':
            player.power_up()
