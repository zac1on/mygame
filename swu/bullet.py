import pygame
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = BULLET_SPEED

    def update(self):
        """Движение пули"""
        self.rect.y += self.speed
        # Удалить пулю, если она вышла за экран
        if self.rect.bottom < 0:
            self.kill()
