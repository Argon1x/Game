import math
import random
from pathlib import Path

import pygame

from asset_paths import (
    BAT_FRAMES_DIR,
    BUG_FRAMES_DIR,
    SCORPION_FRAMES_DIR,
    SLIME_FRAMES_DIR,
    WORM_FRAMES_DIR,
    SOUNDS,
)
from assets_loader import load_sound
from settings import *
from sprite_anim import AnimatedCharacter

_enemy_hit_sound = None
_enemy_death_sound = None
_player_hurt_sound = None

def _get_hit_sound():
    global _enemy_hit_sound
    if _enemy_hit_sound is None:
        _enemy_hit_sound = load_sound(SOUNDS["enemy_hit"], volume=0.4)
    return _enemy_hit_sound

def _get_death_sound():
    global _enemy_death_sound
    if _enemy_death_sound is None:
        _enemy_death_sound = load_sound(SOUNDS["enemy_death"], volume=0.15)
    return _enemy_death_sound

def _get_player_hurt_sound():
    global _player_hurt_sound
    if _player_hurt_sound is None:
        _player_hurt_sound = load_sound(SOUNDS["player_hurt"], volume=0.4)
    return _player_hurt_sound


def _fallback_sprite(size: int, color: tuple[int, int, int]) -> pygame.Surface:
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (size, size), size)
    return surf


ENEMY_TYPES: dict[str, dict] = {
    "slime": {
        "hp": SLIME_HP,
        "speed": SLIME_SPEED,
        "size": SLIME_SIZE,
        "xp": SLIME_XP,
        "damage": SLIME_DAMAGE,
        "frames_dir": SLIME_FRAMES_DIR,
        "fallback_color": RED,
        "unlock_wave": 1,
        "spawn_weight": 1.0,
    },
    "worm": {
        "hp": WORM_HP,
        "speed": WORM_SPEED,
        "size": WORM_SIZE,
        "xp": WORM_XP,
        "damage": WORM_DAMAGE,
        "frames_dir": WORM_FRAMES_DIR,
        "fallback_color": (160, 100, 60),
        "unlock_wave": 2,
        "spawn_weight": 0.85,
    },
    "bat": {
        "hp": BAT_HP,
        "speed": BAT_SPEED,
        "size": BAT_SIZE,
        "xp": BAT_XP,
        "damage": BAT_DAMAGE,
        "frames_dir": BAT_FRAMES_DIR,
        "fallback_color": (80, 60, 120),
        "unlock_wave": 4,
        "spawn_weight": 0.75,
    },
    "bug": {
        "hp": BUG_HP,
        "speed": BUG_SPEED,
        "size": BUG_SIZE,
        "xp": BUG_XP,
        "damage": BUG_DAMAGE,
        "frames_dir": BUG_FRAMES_DIR,
        "fallback_color": (120, 80, 40),
        "unlock_wave": 6,
        "spawn_weight": 0.65,
    },
    "scorpion": {
        "hp": SCORPION_HP,
        "speed": SCORPION_SPEED,
        "size": SCORPION_SIZE,
        "xp": SCORPION_XP,
        "damage": SCORPION_DAMAGE,
        "frames_dir": SCORPION_FRAMES_DIR,
        "fallback_color": (180, 120, 30),
        "unlock_wave": 8,
        "spawn_weight": 0.55,
    },
}


def pick_enemy_type(wave: int) -> str:
    pool = [
        (name, cfg["spawn_weight"])
        for name, cfg in ENEMY_TYPES.items()
        if wave >= cfg["unlock_wave"]
    ]
    if not pool:
        return "slime"

    names, weights = zip(*pool)
    return random.choices(names, weights=weights, k=1)[0]


def _wave_stat_mult(wave: int, per_wave: float) -> float:
    return 1.0 + max(0, wave - 1) * per_wave


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type: str = "slime", player=None, wave: int = 1):
        super().__init__()

        cfg = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["slime"])
        self.enemy_type = enemy_type if enemy_type in ENEMY_TYPES else "slime"
        damage_mult = _wave_stat_mult(wave, ENEMY_DAMAGE_SCALE_PER_WAVE)
        max_speed = (PLAYER_SPEED / FPS) * ENEMY_MAX_SPEED_RATIO

        self.speed = min(cfg["speed"], max_speed)
        wave_mult = _wave_stat_mult(wave, ENEMY_HP_SCALE_PER_WAVE)
        self.hp = max(1, int(cfg["hp"] * wave_mult))
        self.max_hp = self.hp
        self.size = cfg["size"]
        self.xp_value = cfg["xp"]
        self.contact_damage = max(1, int(cfg["damage"] * damage_mult))
        player_level = player.level if player else PLAYER_EASE_UNTIL_LEVEL
        if player_level < PLAYER_EASE_UNTIL_LEVEL:
            self.contact_damage = max(1, int(self.contact_damage * PLAYER_EASE_DAMAGE))
        self.attack_timer = 0
        self.attack_cooldown = max(
            ENEMY_ATTACK_COOLDOWN_MIN,
            ENEMY_ATTACK_COOLDOWN_BASE - (wave - 1),
        )
        self._move_dx = 0.0
        self._move_dy = 0.0
        self._loot_dropped = False

        frames_dir: Path = cfg["frames_dir"]
        if frames_dir.exists() and any(frames_dir.glob("down_*.png")):
            self.animator = AnimatedCharacter(
                frames_dir,
                self.size * 2,
                anim_ticks_per_frame=ENEMY_ANIM_MS_PER_FRAME,
            )
            self.image = self.animator.image
            sprite_w, sprite_h = self.image.get_size()
            self.size = max(sprite_w, sprite_h) // 2
        else:
            self.animator = None
            self.image = _fallback_sprite(self.size, cfg["fallback_color"])

        self.rect = self.image.get_rect()
        self._spawn_near_player(player)

    def _spawn_near_player(self, player) -> None:
        px = player.x if player else WORLD_WIDTH // 2
        py = player.y if player else WORLD_HEIGHT // 2
        spawn_dist = max(SCREEN_WIDTH, SCREEN_HEIGHT) // 2 + 120
        angle = random.uniform(0, math.pi * 2)
        sx = px + math.cos(angle) * spawn_dist
        sy = py + math.sin(angle) * spawn_dist
        sx = max(self.size, min(WORLD_WIDTH - self.size, sx))
        sy = max(self.size, min(WORLD_HEIGHT - self.size, sy))
        self.rect.center = (int(sx), int(sy))
        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)

    @property
    def center_x(self) -> float:
        return self.fx + self.rect.width // 2

    @property
    def center_y(self) -> float:
        return self.fy + self.rect.height // 2

    @property
    def contact_radius(self) -> float:
        return min(self.rect.width, self.rect.height) * ENEMY_CONTACT_RADIUS_SCALE

    def _contact_range(self, player) -> float:
        return self.contact_radius + player.contact_radius

    def take_damage(self, amount, player=None, crystals_group=None, wave_manager=None) -> bool:
        if not self.alive() or self._loot_dropped:
            return False

        self.hp -= amount
        if player is not None and player.vampirism > 0:
            heal = amount * player.vampirism
            player.hp = min(player.max_hp, player.hp + heal)
        hit_sound = _get_hit_sound()
        if hit_sound:
            hit_sound.play()
        if self.hp > 0:
            return False

        death_sound = _get_death_sound()
        if death_sound:
            death_sound.play()
        if player is not None:
            player.score += self.xp_value
        self._drop_loot(crystals_group, wave_manager)
        self.kill()
        return True

    def _drop_loot(self, crystals_group=None, wave_manager=None) -> None:
        if self._loot_dropped:
            return

        self._loot_dropped = True
        if crystals_group is not None:
            from pickups import XPCristal

            crystals_group.add(XPCristal(self.center_x, self.center_y, self.xp_value))
        if wave_manager is not None:
            wave_manager.enemy_killed()

    def update(self, player, tick=1):
        enemy_cx = self.center_x
        enemy_cy = self.center_y

        dx = player.x - enemy_cx
        dy = player.y - enemy_cy
        distance = math.hypot(dx, dy)

        stop_distance = self._contact_range(player)
        moving = distance > stop_distance
        if moving:
            self.fx += (dx / distance) * self.speed
            self.fy += (dy / distance) * self.speed
            self._move_dx = dx
            self._move_dy = dy
        else:
            self._move_dx = 0.0
            self._move_dy = 0.0

        if self.animator:
            topleft = (int(self.fx), int(self.fy))
            self.animator.set_movement(self._move_dx, self._move_dy, moving=moving)
            self.animator.update(tick)
            self.image = self.animator.image
            self.rect = self.image.get_rect(topleft=topleft)
        else:
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

        distance = math.hypot(player.x - self.center_x, player.y - self.center_y)
        if distance < self._contact_range(player):
            if self.attack_timer == 0:
                armor_mult = max(ARMOR_DAMAGE_MIN, player.armor)
                damage = max(1, int(self.contact_damage * armor_mult))
                player.hp -= damage
                self.attack_timer = self.attack_cooldown
                hurt_sound = _get_player_hurt_sound()
                if hurt_sound and hurt_sound.get_num_channels() == 0:
                    hurt_sound.play()


def spawn_enemy(wave: int, player) -> Enemy:
    return Enemy(pick_enemy_type(wave), player, wave)
