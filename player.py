import pygame
import math
from settings import *
from weapons import Knife

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.survival_time = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next = 3
        self.level_up_pending = False

        self.size = PLAYER_SIZE
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, CYAN, (self.size, self.size), self.size)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        self.speed = PLAYER_SPEED
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP

        self.damage_multiplier = 1.0
        self.armor = 0.0
        self.vampirism = 0.0
        self.regen_rate = 0
        self.regen_accumulator = 0.0
        self.pickup_radius = PLAYER_PICKUP_RADIUS
        self.xp_multiplier = 1.0

        self.weapons = [Knife()]

        self.passive_levels = {
            "Speed Boost": 0,
            "Damage Boost": 0,
            "Rapid Fire": 0,
            "Piercing": 0,
            "Max Health": 0,
            "Vampirism": 0,
            "Armor": 0,
            "Regeneration": 0,
            "Magnet": 0,
            "XP Boost": 0,
        }

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        distance = math.hypot(dx, dy)
        if distance > 0:
            self.fx += (dx / distance) * self.speed / FPS
            self.fy += (dy / distance) * self.speed / FPS

        if self.fx < 0: self.fx = 0
        if self.fx > SCREEN_WIDTH - self.size * 2: self.fx = SCREEN_WIDTH - self.size * 2
        if self.fy < 0: self.fy = 0
        if self.fy > SCREEN_HEIGHT - self.size * 2: self.fy = SCREEN_HEIGHT - self.size * 2

        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

    def update(self, tick):
        self.survival_time += tick

        if self.regen_rate > 0 and self.hp < self.max_hp:
            self.regen_accumulator += self.regen_rate * (tick / 1000)
            if self.regen_accumulator >= 1:
                heal_amount = int(self.regen_accumulator)
                self.heal(heal_amount)
                self.regen_accumulator -= heal_amount

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def update_weapons(self, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        for weapon in self.weapons:
            weapon.update(self, enemies, bullets_group, tick, crystals_group, wave_manager)

    @property
    def x(self):
        return self.fx + self.size

    @property
    def y(self):
        return self.fy + self.size

    def draw_ui(self, screen):
        font = pygame.font.SysFont(None, 36)
        font_small = pygame.font.SysFont(None, 28)

        pygame.draw.rect(screen, (80, 80, 80), (17, 17, 206, 22))
        hp_width = int(200 * (self.hp / self.max_hp))
        pygame.draw.rect(screen, (50, 200, 50), (20, 20, hp_width, 16))
        hp_text = font_small.render(f"HP: {int(self.hp)}/{self.max_hp}", True, WHITE)
        screen.blit(hp_text, (20, 42))

        seconds = self.survival_time // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        time_text = font.render(f"{minutes:02}:{seconds:02}", True, WHITE)
        time_rect = time_text.get_rect(centerx=SCREEN_WIDTH // 2, top=20)
        screen.blit(time_text, time_rect)

        xp_bar_x = SCREEN_WIDTH - 220
        pygame.draw.rect(screen, (80, 80, 80), (xp_bar_x - 3, 17, 206, 22))
        xp_width = int(200 * (self.xp / self.xp_to_next))
        pygame.draw.rect(screen, (100, 200, 255), (xp_bar_x, 20, xp_width, 16))

        lvl_text = font_small.render(f"Lv.{self.level}", True, (255, 220, 0))
        screen.blit(lvl_text, (xp_bar_x, 42))