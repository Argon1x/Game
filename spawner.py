from enemies import spawn_enemy
from settings import SPAWN_COOLDOWN_MS


class Spawner:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_cooldown = SPAWN_COOLDOWN_MS

    def update(self, enemies_group, wave_manager, player, tick=1):
        if wave_manager.in_pause:
            return

        if len(enemies_group) >= wave_manager.max_enemies:
            return

        total_spawned = wave_manager.enemies_killed + len(enemies_group)
        if total_spawned >= wave_manager.enemies_to_spawn:
            return

        if self.spawn_timer > 0:
            self.spawn_timer -= tick
        else:
            enemies_group.add(spawn_enemy(wave_manager.wave, player))
            self.spawn_timer = self.spawn_cooldown
