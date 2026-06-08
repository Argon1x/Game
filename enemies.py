import pygame
import math
import random
from settings import *


class Slime(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.speed = SLIME_SPEED
        self.hp = SLIME_HP
        self.size = SLIME_SIZE
        self.attack_timer = 0
        self.attack_cooldown = 20

        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (self.size, self.size), self.size)
        self.rect = self.image.get_rect()

        side = random.randint(0, 3)
        if side == 0:
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = -self.size * 2
        elif side == 1:
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = SCREEN_HEIGHT
        elif side == 2:
            self.rect.x = -self.size * 2
            self.rect.y = random.randint(0, SCREEN_HEIGHT)
        else:
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT)

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

    def update(self, player):
        enemy_cx = self.fx + self.size
        enemy_cy = self.fy + self.size

        dx = player.x - enemy_cx
        dy = player.y - enemy_cy
        distance = math.hypot(dx, dy)

        stop_distance = self.size + player.size
        if distance > stop_distance:
            self.fx += (dx / distance) * self.speed
            self.fy += (dy / distance) * self.speed

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

    def separate(self, enemies_group):
        for other in enemies_group:
            if other is self:
                continue
            dx = self.fx - other.fx
            dy = self.fy - other.fy
            distance = math.hypot(dx, dy)
            min_distance = self.size + other.size
            if 0 < distance < min_distance:
                push = (min_distance - distance) / distance * 0.05
                self.fx += dx * push
                self.fy += dy * push

    def check_collision_with_player(self, player):
        if self.attack_timer > 0:
            self.attack_timer -= 1

        enemy_cx = self.fx + self.size
        enemy_cy = self.fy + self.size

        distance = math.hypot(player.x - enemy_cx, player.y - enemy_cy)
        if distance < self.size + player.size:
            if self.attack_timer == 0:
                player.hp -= SLIME_DAMAGE
                self.attack_timer = self.attack_cooldown