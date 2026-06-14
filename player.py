import pygame
import math

from asset_paths import PLAYER_FRAMES_DIR
from settings import *
from sprite_anim import AnimatedCharacter
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
        self._last_dx = 0.0
        self._last_dy = 0.0

        self.animator = AnimatedCharacter(
            PLAYER_FRAMES_DIR,
            self.size * 2,
            anim_ticks_per_frame=PLAYER_ANIM_MS_PER_FRAME,
        )
        self.image = self.animator.image
        sprite_w, sprite_h = self.image.get_size()
        self.size = max(sprite_w, sprite_h) // 2

        self.rect = self.image.get_rect(center=(WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

        self.speed = PLAYER_SPEED
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP

        self.damage_multiplier = 1.0
        self.armor = 1.0
        self.vampirism = 0.0
        self.regen = False
        self.bullet_pierce = False
        self.pickup_radius = PLAYER_PICKUP_RADIUS
        self.xp_multiplier = 1.0

        self.weapons = [Knife()]

    def handle_input(self, enabled: bool = True):
        if not enabled:
            self.animator.set_movement(0, 0, moving=False)
            return

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1

        distance = math.hypot(dx, dy)
        moving = distance > 0
        if moving:
            self.fx += (dx / distance) * self.speed / FPS
            self.fy += (dy / distance) * self.speed / FPS
            self._last_dx = dx
            self._last_dy = dy

        if self.fx < 0:
            self.fx = 0
        if self.fx > WORLD_WIDTH - self.rect.width:
            self.fx = WORLD_WIDTH - self.rect.width
        if self.fy < 0:
            self.fy = 0
        if self.fy > WORLD_HEIGHT - self.rect.height:
            self.fy = WORLD_HEIGHT - self.rect.height

        self.animator.set_movement(self._last_dx, self._last_dy, moving=moving)
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)

    def update(self, tick):
        self.survival_time += tick
        if self.regen and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + tick * PLAYER_REGEN_PER_MS)
        center = self.rect.center
        self.animator.update(tick)
        self.image = self.animator.image
        self.rect = self.image.get_rect(center=center)

    def update_weapons(self, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        for weapon in self.weapons:
            weapon.update(self, enemies, bullets_group, tick, crystals_group, wave_manager)

    @property
    def x(self):
        return self.fx + self.rect.width // 2

    @property
    def y(self):
        return self.fy + self.rect.height // 2

    @property
    def contact_radius(self) -> float:
        return min(self.rect.width, self.rect.height) * ENEMY_CONTACT_RADIUS_SCALE

    def draw_ui(self, screen):
        from ui_elements import _menu_font

        hud_h = 68
        pad_x = 18
        bar_w = 152
        bar_h = 14
        bar_y = (hud_h - bar_h) // 2
        text_y = bar_y + (bar_h - 18) // 2

        font_label = _menu_font(18, bold=True)
        font_value = _menu_font(17)

        def draw_row(x, label, value, ratio, label_color, fill_color, value_color):
            label_s = font_label.render(label, True, label_color)
            value_s = font_value.render(value, True, value_color)
            screen.blit(label_s, (x, text_y))
            bx = x + label_s.get_width() + 10
            outer = pygame.Rect(bx, bar_y, bar_w, bar_h)
            pygame.draw.rect(screen, (22, 18, 14), outer, border_radius=4)
            pygame.draw.rect(screen, SAND, outer, 1, border_radius=4)
            inner_w = max(0, int((bar_w - 4) * max(0.0, min(1.0, ratio))))
            if inner_w > 0:
                pygame.draw.rect(screen, fill_color, (bx + 2, bar_y + 2, inner_w, bar_h - 4), border_radius=3)
            screen.blit(value_s, (bx + bar_w + 8, text_y))

        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        draw_row(pad_x, "HP", f"{int(self.hp)}/{self.max_hp}", hp_ratio, (130, 220, 130), (58, 178, 68), (220, 245, 220))

        seconds = self.survival_time // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        time_surf = _menu_font(28, bold=True).render(f"{minutes:02}:{seconds:02}", True, WHITE)
        tw, th = time_surf.get_size()
        box_w, box_h = tw + 24, th + 10
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (hud_h - box_h) // 2
        timer_box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        timer_box.fill((62, 46, 32, 110))
        pygame.draw.rect(timer_box, (*SAND, 90), timer_box.get_rect(), 1, border_radius=6)
        screen.blit(timer_box, (box_x, box_y))
        screen.blit(time_surf, time_surf.get_rect(center=(SCREEN_WIDTH // 2, hud_h // 2)))

        xp_ratio = self.xp / self.xp_to_next if self.xp_to_next > 0 else 0
        lv_label = f"Lv.{self.level}"
        xp_value = f"{self.xp}/{self.xp_to_next}"
        lv_s = font_label.render(lv_label, True, YELLOW)
        val_s = font_value.render(xp_value, True, (215, 228, 255))
        row_w = lv_s.get_width() + 10 + bar_w + 8 + val_s.get_width()
        draw_row(SCREEN_WIDTH - pad_x - row_w, lv_label, xp_value, xp_ratio, YELLOW, (68, 158, 220), (215, 228, 255))
