import pygame
import math
from settings import *
from pickups import XPCristal

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, damage=None, speed=None, color=None, size=None):
        super().__init__()

        self.size = size if size else BULLET_SIZE
        self.damage = damage if damage else BULLET_DAMAGE
        self.speed = speed if speed else BULLET_SPEED
        self.color = color if color else YELLOW

        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))

        self.fx = float(x)
        self.fy = float(y)

        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = 0

    def update(self):
        self.fx += self.vx
        self.fy += self.vy
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

        if self.fx < 0 or self.fx > SCREEN_WIDTH:
            self.kill()
        if self.fy < 0 or self.fy > SCREEN_HEIGHT:
            self.kill()

    def check_collision_with_enemy(self, enemy, player, crystals_group, wave_manager):
        if not self.alive():
            return

        bullet_cx = self.fx + self.size
        bullet_cy = self.fy + self.size
        enemy_cx = enemy.fx + enemy.size
        enemy_cy = enemy.fy + enemy.size

        distance = math.hypot(enemy_cx - bullet_cx, enemy_cy - bullet_cy)
        if distance < self.size + enemy.size:
            enemy.hp -= self.damage
            if enemy.hp <= 0:
                crystals_group.add(XPCristal(enemy_cx, enemy_cy))
                wave_manager.enemy_killed()
                enemy.kill()
            self.kill()