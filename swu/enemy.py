import pygame
import random
from settings import *


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = random.randrange(ENEMY_SPEED, ENEMY_SPEED + 2)
        self.speed_y = random.randrange(1, 3)

    def update(self):
        """Движение врага"""
        self.rect.y += self.speed_y
        
        # Движение влево-вправо
        self.rect.x += self.speed
        
        # Отскок от краев
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speed = -self.speed
        
        # Удалить врага, если он вышел за экран
        if self.rect.top > HEIGHT + 10:
            self.kill()
