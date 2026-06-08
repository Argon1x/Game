import pygame
import math
from settings import *

class XPCristal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.value = SLIME_XP
        self.size = 8
        self.collect_delay = 500

        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (0, 200, 255), [
            (self.size, 0),
            (self.size * 2, self.size),
            (self.size, self.size * 2),
            (0, self.size)
        ])
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))

        self.fx = float(x)
        self.fy = float(y)

    def update(self, player, collect_all=False):
        dx = player.x - self.fx
        dy = player.y - self.fy
        distance = math.hypot(dx, dy)

        if self.collect_delay > 0:
            self.collect_delay -= 16

        if collect_all:
            if distance > 0:
                speed = max(3, distance * 0.15)
                self.fx += (dx / distance) * speed
                self.fy += (dy / distance) * speed

        elif distance < player.pickup_radius:
            if distance > 0:
                speed = max(1.3, distance * 0.08)
                self.fx += (dx / distance) * speed
                self.fy += (dy / distance) * speed

        else:
            if distance > 0:
                self.fx += (dx / distance) * 0.25
                self.fy += (dy / distance) * 0.25

        if distance < player.size and self.collect_delay <= 0:
            player.xp += int(self.value * player.xp_multiplier)
            if player.xp >= player.xp_to_next:
                player.xp -= player.xp_to_next
                player.level += 1
                extra = (player.level // 10)
                increase = 2 + extra
                player.xp_to_next += increase
                player.level_up_pending = True
            self.kill()

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)