from enemies import spawn_enemy


class Spawner:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_cooldown = 0
        self._last_wave = None

    def _calc_cooldown(self, wave: int) -> int:
        return max(300, 1200 - wave * 200)

    def update(self, enemies_group, wave_manager, player, tick=1):
        if wave_manager.in_pause:
            return

        if len(enemies_group) >= wave_manager.max_enemies:
            return

        total_spawned = wave_manager.enemies_killed + len(enemies_group)
        if total_spawned >= wave_manager.enemies_to_spawn:
            return

        if self._last_wave != wave_manager.wave:
            self._last_wave = wave_manager.wave
            self.spawn_cooldown = self._calc_cooldown(wave_manager.wave)
            self.spawn_timer = 0

        if self.spawn_timer > 0:
            self.spawn_timer -= tick
        else:
            enemies_group.add(spawn_enemy(wave_manager.wave, player))
            self.spawn_timer = self.spawn_cooldown
