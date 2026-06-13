import pygame
from enemies import Slime
from settings import *


class Spawner:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_cooldown = 72

    def _calculate_cooldown(self, wave_manager):
        total = wave_manager.enemies_to_spawn
        if total >= 30:
            return FPS // 2 
        else:
            return max(1, int((15 * FPS) / total))

    def update(self, enemies_group, wave_manager):
        if wave_manager.in_pause:
            return

        if len(enemies_group) >= wave_manager.max_enemies:
            return

        total_spawned = wave_manager.enemies_killed + len(enemies_group)
        if total_spawned >= wave_manager.enemies_to_spawn:
            return

        if self.spawn_timer > 0:
            self.spawn_timer -= 1
        else:
            enemies_group.add(Slime())
            self.spawn_timer = self._calculate_cooldown(wave_manager)