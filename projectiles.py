import math

import pygame

from asset_paths import PROJECTILE_SPRITES
from assets_loader import load_sprite
from settings import *

_projectile_cache: dict[tuple[str, int], pygame.Surface | None] = {}
_blade_angles: dict[int, float] = {}


def _projectile_sprite(kind: str, size: int) -> pygame.Surface | None:
    key = (kind, size)
    if key not in _projectile_cache:
        path = PROJECTILE_SPRITES.get(kind)
        _projectile_cache[key] = load_sprite(path, size * 2) if path else None
    return _projectile_cache[key]


def _knife_blade_angle(surface: pygame.Surface) -> float:
    surface_id = id(surface)
    if surface_id in _blade_angles:
        return _blade_angles[surface_id]

    w, h = surface.get_size()
    cx, cy = w / 2, h / 2
    tip_x = tip_y = tip_n = 0.0
    tail_x = tail_y = tail_n = 0.0

    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y))[3] <= 30:
                continue
            if y < cy:
                tip_x += x
                tip_y += y
                tip_n += 1
            elif y > cy:
                tail_x += x
                tail_y += y
                tail_n += 1

    if tip_n > 0 and tail_n > 0:
        angle = math.degrees(
            math.atan2(
                tip_y / tip_n - tail_y / tail_n,
                tip_x / tip_n - tail_x / tail_n,
            )
        )
    else:
        best_dist = 0.0
        angle = 0.0
        for y in range(h):
            for x in range(w):
                if surface.get_at((x, y))[3] <= 30:
                    dx = x - cx
                    dy = y - cy
                    dist = dx * dx + dy * dy
                    if dist > best_dist:
                        best_dist = dist
                        angle = math.degrees(math.atan2(dy, dx))

    _blade_angles[surface_id] = angle
    return angle


def _knife_forward_error(surface: pygame.Surface, flight_angle: float) -> float:
    w, h = surface.get_size()
    center_x, center_y = w / 2, h / 2
    flight_rad = math.radians(flight_angle)
    dir_x = math.cos(flight_rad)
    dir_y = math.sin(flight_rad)

    best_proj = float("-inf")
    tip_angle = flight_angle
    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y))[3] <= 30:
                continue
            proj = (x - center_x) * dir_x + (y - center_y) * dir_y
            if proj > best_proj:
                best_proj = proj
                tip_angle = math.degrees(math.atan2(y - center_y, x - center_x))

    if best_proj == float("-inf"):
        return 180.0

    diff = (tip_angle - flight_angle + 180) % 360 - 180
    return abs(diff)


def _rotate_knife_sprite(surface: pygame.Surface, dx: float, dy: float) -> pygame.Surface:
    if dx == 0 and dy == 0:
        return surface

    flight_angle = math.degrees(math.atan2(dy, dx))
    blade_angle = _knife_blade_angle(surface)

    best_surface = surface
    best_error = float("inf")

    for rotation in (flight_angle + blade_angle, blade_angle - flight_angle):
        rotated = pygame.transform.rotate(surface, rotation)
        error = _knife_forward_error(rotated, flight_angle)
        if error < best_error:
            best_error = error
            best_surface = rotated

    return best_surface


class Bullet(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        target_x,
        target_y,
        damage=None,
        speed=None,
        color=None,
        size=None,
        sprite_kind: str = "knife",
    ):
        super().__init__()

        self.size = size if size else BULLET_SIZE
        self.damage = damage if damage is not None else 0
        self.speed = speed if speed else BULLET_SPEED
        self.color = color if color else YELLOW

        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)

        base_sprite = _projectile_sprite(sprite_kind, self.size)
        if base_sprite:
            if sprite_kind == "knife" and distance > 0:
                self.image = _rotate_knife_sprite(base_sprite, dx, dy)
            else:
                self.image = base_sprite
            self.size = max(self.image.get_width(), self.image.get_height()) // 2
        else:
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)

        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.fx = float(x)
        self.fy = float(y)

        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = 0
            self.vy = 0

        self.hit_enemies: set[int] = set()

    def update(self):
        self.fx += self.vx
        self.fy += self.vy
        self.rect.center = (int(self.fx), int(self.fy))

        if self.fx < 0 or self.fx > WORLD_WIDTH:
            self.kill()
        if self.fy < 0 or self.fy > WORLD_HEIGHT:
            self.kill()

    def check_collision_with_enemy(self, enemy, player, crystals_group, wave_manager):
        if not self.alive() or not enemy.alive():
            return

        bullet_cx = self.fx
        bullet_cy = self.fy
        enemy_cx = enemy.center_x
        enemy_cy = enemy.center_y

        distance = math.hypot(enemy_cx - bullet_cx, enemy_cy - bullet_cy)
        enemy_id = id(enemy)
        if distance < self.size + enemy.size and enemy_id not in self.hit_enemies:
            self.hit_enemies.add(enemy_id)
            enemy.take_damage(self.damage, player, crystals_group, wave_manager)
            if len(self.hit_enemies) > player.bullet_pierce:
                self.kill()
