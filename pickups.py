import pygame
import math

from asset_paths import XP_CRYSTAL, SOUNDS
from assets_loader import load_sprite, load_sound

_pickup_sound = None
_levelup_sound = None

def _get_pickup_sound():
    global _pickup_sound
    if _pickup_sound is None:
        _pickup_sound = load_sound(SOUNDS["pickup"], volume=0.3)
    return _pickup_sound

def _get_levelup_sound():
    global _levelup_sound
    if _levelup_sound is None:
        _levelup_sound = load_sound(SOUNDS["levelup"], volume=0.6)
    return _levelup_sound
from settings import *

_xp_sprite = None


def _get_xp_sprite(size: int) -> pygame.Surface | None:
    global _xp_sprite
    if _xp_sprite is None:
        _xp_sprite = load_sprite(XP_CRYSTAL, size * 2)
    return _xp_sprite


class XPCristal(pygame.sprite.Sprite):
    def __init__(self, x, y, value: int | None = None):
        super().__init__()

        self.value = value if value is not None else SLIME_XP
        self.size = 8
        self.collect_delay = 500

        sprite = _get_xp_sprite(self.size)
        if sprite:
            self.image = sprite
            self.size = max(sprite.get_width(), sprite.get_height()) // 2
        else:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.image,
                (0, 200, 255),
                [
                    (self.size, 0),
                    (self.size * 2, self.size),
                    (self.size, self.size * 2),
                    (0, self.size),
                ],
            )

        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.fx = float(x)
        self.fy = float(y)

    def update(self, player, collect_all=False, tick=16):
        dx = player.x - self.fx
        dy = player.y - self.fy
        distance = math.hypot(dx, dy)

        if self.collect_delay > 0:
            self.collect_delay -= tick

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
            sound = _get_pickup_sound()
            if sound:
                sound.play()
            player.xp += int(self.value * player.xp_multiplier)
            if player.xp >= player.xp_to_next:
                player.xp -= player.xp_to_next
                player.level += 1
                increase = 1 if player.level <= 2 else 2
                player.xp_to_next += increase
                player.level_up_pending = True
                levelup_sound = _get_levelup_sound()
                if levelup_sound:
                    levelup_sound.play()
            self.kill()

        self.rect.center = (int(self.fx), int(self.fy))
