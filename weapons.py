import pygame
import math
from settings import *
from projectiles import Bullet


class Knife:
    def __init__(self):
        self.level = 1
        self.damage = 10
        self.cooldown = 1300
        self.timer = 0

    def update(self, player, enemies, bullets_group, tick, crystals_group=None, wave_manager=None):
        if self.timer > 0:
            self.timer -= tick
            return

        closest = None
        closest_dist = float('inf')

        for enemy in enemies:
            if not enemy.alive():
                continue
            dist = math.hypot(enemy.fx - player.x, enemy.fy - player.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest:
            bullet = Bullet(
                player.x, player.y,
                closest.fx + closest.size,
                closest.fy + closest.size,
                self.damage * player.damage_multiplier
            )
            bullets_group.add(bullet)
            self.timer = self.cooldown

    def level_up(self):
        self.level += 1
        self.damage += 5
        self.cooldown -= 100
        self.cooldown = max(400, self.cooldown)


class MagicOrb:
    def __init__(self):
        self.level = 1
        self.damage = 15
        self.radius = 50
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
                enemy_cx = enemy.fx + enemy.size
                enemy_cy = enemy.fy + enemy.size
                dist = math.hypot(enemy_cx - orb_x, enemy_cy - orb_y)
                enemy_id = id(enemy)

                if dist < 15 + enemy.size and enemy_id not in self.hit_cooldown:
                    enemy.hp -= self.damage * player.damage_multiplier
                    self.hit_cooldown[enemy_id] = 500
                    if enemy.hp <= 0:
                        if crystals_group is not None:
                            from pickups import XPCristal
                            crystals_group.add(XPCristal(enemy_cx, enemy_cy))
                        if wave_manager:
                            wave_manager.enemy_killed()
                        enemy.kill()

    def draw(self, screen, player):
        for i in range(self.orb_count):
            angle_offset = 360 / self.orb_count * i
            orb_angle = math.radians(self.angle + angle_offset)
            orb_x = int(player.x + math.cos(orb_angle) * self.radius)
            orb_y = int(player.y + math.sin(orb_angle) * self.radius)
            pygame.draw.circle(screen, (100, 150, 255), (orb_x, orb_y), 12)
            pygame.draw.circle(screen, (200, 220, 255), (orb_x, orb_y), 6)

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
        self.radius = 30
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
            enemy_cx = enemy.fx + enemy.size
            enemy_cy = enemy.fy + enemy.size
            dist = math.hypot(enemy_cx - player.x, enemy_cy - player.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest:
            target_x = closest.fx + closest.size
            target_y = closest.fy + closest.size

            self.effects.append({'x': target_x, 'y': target_y, 'timer': 400})

            for enemy in list(enemies):
                if not enemy.alive():
                    continue
                enemy_cx = enemy.fx + enemy.size
                enemy_cy = enemy.fy + enemy.size
                dist = math.hypot(enemy_cx - target_x, enemy_cy - target_y)
                if dist < self.radius:
                    enemy.hp -= self.damage * player.damage_multiplier
                    if enemy.hp <= 0:
                        if crystals_group:
                            from pickups import XPCristal
                            crystals_group.add(XPCristal(enemy_cx, enemy_cy))
                        if wave_manager:
                            wave_manager.enemy_killed()
                        enemy.kill()

            self.timer = self.cooldown

    def draw(self, screen, player):
        for effect in self.effects:
            progress = 1 - (effect['timer'] / 400)
            radius = int(self.radius * progress)
            color = (200, 150, 50)
            if radius > 0:
                pygame.draw.circle(screen, color, (int(effect['x']), int(effect['y'])), radius, 3)
                for i in range(6):
                    angle = math.radians(i * 60 + progress * 30)
                    sx = int(effect['x'] + math.cos(angle) * radius)
                    sy = int(effect['y'] + math.sin(angle) * radius)
                    pygame.draw.line(screen, color,
                        (int(effect['x']), int(effect['y'])),
                        (sx, sy), 2)

    def level_up(self):
        self.level += 1
        self.damage += 10
        self.cooldown = max(600, self.cooldown - 300)
        self.radius += 15


class Boomerang:
    def __init__(self):
        self.level = 1
        self.damage = 20
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
            enemy_cx = enemy.fx + enemy.size
            enemy_cy = enemy.fy + enemy.size
            dist = math.hypot(enemy_cx - player.x, enemy_cy - player.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        if closest:
            dx = (closest.fx + closest.size) - player.x
            dy = (closest.fy + closest.size) - player.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                speed = 3
                self.projectiles.append({
                    'x': player.x, 'y': player.y,
                    'vx': (dx / dist) * speed,
                    'vy': (dy / dist) * speed,
                    'state': 'outgoing',
                    'traveled': 0,
                    'max_dist': 400,
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

        # Начинаем новую серию
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
                speed = 8
                boomerang['x'] += (dx / dist) * speed
                boomerang['y'] += (dy / dist) * speed

            for enemy in list(enemies):
                if not enemy.alive():
                    continue
                enemy_cx = enemy.fx + enemy.size
                enemy_cy = enemy.fy + enemy.size
                dist = math.hypot(enemy_cx - boomerang['x'], enemy_cy - boomerang['y'])
                enemy_id = id(enemy)

                if dist < 20 + enemy.size and enemy_id not in boomerang['hit_enemies']:
                    boomerang['hit_enemies'].add(enemy_id)
                    enemy.hp -= self.damage * player.damage_multiplier
                    if enemy.hp <= 0:
                        if crystals_group:
                            from pickups import XPCristal
                            crystals_group.add(XPCristal(enemy_cx, enemy_cy))
                        if wave_manager:
                            wave_manager.enemy_killed()
                        enemy.kill()

    def draw(self, screen, player):
        for boomerang in self.projectiles:
            boomerang['angle'] = (boomerang['angle'] + 10) % 360
            x = int(boomerang['x'])
            y = int(boomerang['y'])
            angle = math.radians(boomerang['angle'])
            points = []
            for i in range(8):
                a = angle + math.radians(i * 20)
                px = x + int(math.cos(a) * 20)
                py = y + int(math.sin(a) * 14)
                points.append((px, py))
            if len(points) > 1:
                pygame.draw.lines(screen, (150, 100, 50), False, points, 3)
            pygame.draw.circle(screen, (200, 160, 80), (x, y), 6)

    def level_up(self):
        self.level += 1
        self.damage += 8
        self.cooldown = max(1000, self.cooldown - 200)
        self.boomerang_count += 1