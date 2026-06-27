import pygame
import math

from asset_paths import PROJECTILE_SPRITES, SOUNDS
from assets_loader import load_sprite, load_sound
from settings import *
from projectiles import Bullet

_weapon_sprite_cache: dict[tuple[str, int], pygame.Surface | None] = {}


def _weapon_sprite(kind: str, size: int) -> pygame.Surface | None:
    key = (kind, size)
    if key not in _weapon_sprite_cache:
        path = PROJECTILE_SPRITES.get(kind)
        _weapon_sprite_cache[key] = load_sprite(path, size * 2) if path else None
    return _weapon_sprite_cache[key]


class Knife:
    def __init__(self):
        self.level = 1
        self.damage = 8
        self.cooldown = 1700
        self.timer = 0
        self._sound = load_sound(SOUNDS["knife_shoot"], volume=0.4)

    def update(self, player, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        if self.timer > 0:
            self.timer -= tick
            return

        closest = None
        closest_dist = float('inf')

        for enemy in enemies:
            if not enemy.alive():
                continue
            dist = math.hypot(enemy.center_x - player.x, enemy.center_y - player.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest:
            enemy_cx = closest.center_x
            enemy_cy = closest.center_y
            bullet = Bullet(
                player.x,
                player.y,
                enemy_cx,
                enemy_cy,
                self.damage * player.damage_multiplier,
            )
            bullets_group.add(bullet)
            self.timer = self.cooldown
            if self._sound:
                self._sound.play()

    def level_up(self):
        self.level += 1
        self.damage += 5
        self.cooldown -= 100
        self.cooldown = max(400, self.cooldown)


class MagicOrb:
    def __init__(self):
        self.level = 1
        self.damage = 11
        self.radius = WEAPON_ORB_RADIUS
        self.speed = 2
        self.orb_count = 1
        self.angle = 0
        self.hit_cooldown = {}

    def update(self, player, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360

        for enemy_id in list(self.hit_cooldown):
            self.hit_cooldown[enemy_id] -= tick
            if self.hit_cooldown[enemy_id] <= 0:
                del self.hit_cooldown[enemy_id]

        for i in range(self.orb_count):
            angle_offset = 360 / self.orb_count * i
            orb_angle = math.radians(self.angle + angle_offset)
            orb_x = player.x + math.cos(orb_angle) * self.radius
            orb_y = player.y + math.sin(orb_angle) * self.radius

            for enemy in list(enemies):
                if not enemy.alive():
                    continue
                enemy_cx = enemy.center_x
                enemy_cy = enemy.center_y
                dist = math.hypot(enemy_cx - orb_x, enemy_cy - orb_y)
                enemy_id = id(enemy)

                if dist < 22 + enemy.size and enemy_id not in self.hit_cooldown:
                    self.hit_cooldown[enemy_id] = 750
                    enemy.take_damage(
                        self.damage * player.damage_multiplier,
                        player,
                        crystals_group,
                        wave_manager,
                    )

    def draw(self, screen, player, camera=None):
        orb_sprite = _weapon_sprite("orb", WEAPON_ORB_SIZE)
        for i in range(self.orb_count):
            angle_offset = 360 / self.orb_count * i
            orb_angle = math.radians(self.angle + angle_offset)
            orb_x = player.x + math.cos(orb_angle) * self.radius
            orb_y = player.y + math.sin(orb_angle) * self.radius
            if camera:
                orb_x, orb_y = camera.apply(orb_x, orb_y)
            else:
                orb_x, orb_y = int(orb_x), int(orb_y)
            if orb_sprite:
                rect = orb_sprite.get_rect(center=(orb_x, orb_y))
                screen.blit(orb_sprite, rect)
            else:
                pygame.draw.circle(screen, (100, 150, 255), (orb_x, orb_y), 16)
                pygame.draw.circle(screen, (200, 220, 255), (orb_x, orb_y), 8)

    def level_up(self):
        self.level += 1
        self.damage += 5
        if self.orb_count < 6:
            self.orb_count += 1


class SandSpike:
    def __init__(self):
        self.level = 1
        self.damage = 25
        self.cooldown = 3000
        self.timer = 0
        self.radius = 36
        self.effects = []

    def update(self, player, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        if self.timer > 0:
            self.timer -= tick

        for effect in self.effects[:]:
            effect['timer'] -= tick
            if effect['timer'] <= 0:
                self.effects.remove(effect)

        if self.timer > 0:
            return

        closest = None
        closest_dist = float('inf')
        for enemy in enemies:
            if not enemy.alive():
                continue
            enemy_cx = enemy.center_x
            enemy_cy = enemy.center_y
            dist = math.hypot(enemy_cx - player.x, enemy_cy - player.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest:
            target_x = closest.center_x
            target_y = closest.center_y

            self.effects.append({'x': target_x, 'y': target_y, 'timer': 400})

            for enemy in list(enemies):
                if not enemy.alive():
                    continue
                enemy_cx = enemy.center_x
                enemy_cy = enemy.center_y
                dist = math.hypot(enemy_cx - target_x, enemy_cy - target_y)
                if dist < self.radius:
                    enemy.take_damage(
                        self.damage * player.damage_multiplier,
                        player,
                        crystals_group,
                        wave_manager,
                    )

            self.timer = self.cooldown

    def draw(self, screen, player, camera=None):
        spike_sprite = _weapon_sprite("spike", WEAPON_SPIKE_SIZE)
        for effect in self.effects:
            progress = 1 - (effect["timer"] / 400)
            radius = int(self.radius * progress)
            if radius <= 0:
                continue
            ex, ey = effect["x"], effect["y"]
            if camera:
                ex, ey = camera.apply(ex, ey)
            else:
                ex, ey = int(ex), int(ey)
            center = (ex, ey)
            if spike_sprite:
                scaled = pygame.transform.smoothscale(
                    spike_sprite,
                    (max(8, radius), max(8, radius)),
                )
                screen.blit(scaled, scaled.get_rect(center=center))
            else:
                color = (200, 150, 50)
                pygame.draw.circle(screen, color, center, radius, 3)
                for i in range(6):
                    angle = math.radians(i * 60 + progress * 30)
                    sx = int(ex + math.cos(angle) * radius)
                    sy = int(ey + math.sin(angle) * radius)
                    pygame.draw.line(screen, color, center, (sx, sy), 2)

    def level_up(self):
        self.level += 1
        self.damage += 10
        self.cooldown = max(600, self.cooldown - 300)
        self.radius += 15


class Boomerang:
    def __init__(self):
        self.level = 1
        self.damage = 10
        self.cooldown = 2500
        self.timer = 0
        self.boomerang_count = 1
        self.launch_timer = 0
        self.pending_launches = 0
        self.projectiles = []

    def _launch(self, player, enemies):
        closest = None
        closest_dist = float('inf')
        for enemy in enemies:
            if not enemy.alive():
                continue
            enemy_cx = enemy.center_x
            enemy_cy = enemy.center_y
            dist = math.hypot(enemy_cx - player.x, enemy_cy - player.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest:
            dx = closest.center_x - player.x
            dy = closest.center_y - player.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                speed = 3
                self.projectiles.append({
                    'x': player.x, 'y': player.y,
                    'vx': (dx / dist) * speed,
                    'vy': (dy / dist) * speed,
                    'state': 'outgoing',
                    'traveled': 0,
                    'max_dist': WEAPON_BOOMERANG_MAX_DIST,
                    'hit_enemies': set(),
                    'timer': 5000,
                    'angle': 0
                })

    def update(self, player, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        if self.timer > 0:
            self.timer -= tick

        if self.launch_timer > 0:
            self.launch_timer -= tick

        if self.pending_launches > 0 and self.launch_timer <= 0:
            self._launch(player, enemies)
            self.pending_launches -= 1
            self.launch_timer = 400

        if self.timer <= 0 and self.pending_launches == 0 and len(self.projectiles) == 0:
            self.pending_launches = self.boomerang_count
            self.timer = self.cooldown

        for boomerang in self.projectiles[:]:
            boomerang['timer'] -= tick

            if boomerang['state'] == 'outgoing':
                boomerang['x'] += boomerang['vx']
                boomerang['y'] += boomerang['vy']
                boomerang['traveled'] += math.hypot(boomerang['vx'], boomerang['vy'])
                if boomerang['traveled'] >= boomerang['max_dist']:
                    boomerang['state'] = 'returning'

            elif boomerang['state'] == 'returning':
                dx = player.x - boomerang['x']
                dy = player.y - boomerang['y']
                dist = math.hypot(dx, dy)
                if dist < 15:
                    self.projectiles.remove(boomerang)
                    continue
                if dist == 0:
                    continue
                speed = 8
                boomerang['x'] += (dx / dist) * speed
                boomerang['y'] += (dy / dist) * speed

            for enemy in list(enemies):
                if not enemy.alive():
                    continue
                enemy_cx = enemy.center_x
                enemy_cy = enemy.center_y
                dist = math.hypot(enemy_cx - boomerang['x'], enemy_cy - boomerang['y'])
                enemy_id = id(enemy)

                if dist < WEAPON_BOOMERANG_HIT_RADIUS + enemy.size and enemy_id not in boomerang['hit_enemies']:
                    boomerang['hit_enemies'].add(enemy_id)
                    enemy.take_damage(
                        self.damage * player.damage_multiplier,
                        player,
                        crystals_group,
                        wave_manager,
                    )

    def draw(self, screen, player, camera=None):
        boomerang_sprite = _weapon_sprite("boomerang", WEAPON_BOOMERANG_SIZE)
        for boomerang in self.projectiles:
            boomerang["angle"] = (boomerang["angle"] + 10) % 360
            x, y = boomerang["x"], boomerang["y"]
            if camera:
                x, y = camera.apply(x, y)
            else:
                x, y = int(x), int(y)
            if boomerang_sprite:
                rotated = pygame.transform.rotate(boomerang_sprite, -boomerang["angle"])
                screen.blit(rotated, rotated.get_rect(center=(x, y)))
            else:
                angle = math.radians(boomerang["angle"])
                points = []
                for i in range(8):
                    a = angle + math.radians(i * 20)
                    px = x + int(math.cos(a) * 24)
                    py = y + int(math.sin(a) * 18)
                    points.append((px, py))
                if len(points) > 1:
                    pygame.draw.lines(screen, (150, 100, 50), False, points, 3)
                pygame.draw.circle(screen, (200, 160, 80), (x, y), 8)

    def level_up(self):
        self.level += 1
        self.damage += 5
        self.cooldown = max(1000, self.cooldown - 200)
        self.boomerang_count += 1