from settings import *

class WaveManager:
    def __init__(self):
        self.wave = 1
        self.enemies_to_spawn = 15
        self.enemies_killed = 0
        self.wave_complete = False
        self.collect_all = False
        self.in_pause = True
        self.max_enemies = 30
        self.phase = 4
        self.phase_timer = 0

    def enemy_killed(self):
        self.enemies_killed += 1
        if self.enemies_killed >= self.enemies_to_spawn:
            self.wave_complete = True
            self.phase = 1
            self.phase_timer = 0
            self.in_pause = True

    def update(self, tick):
        if not self.in_pause:
            return

        self.phase_timer += tick

        if self.phase == 1:
            if self.phase_timer >= 1000:
                self.phase = 2
                self.phase_timer = 0
                self.collect_all = True

        elif self.phase == 2:
            if self.phase_timer >= 1500:
                self.phase = 3
                self.phase_timer = 0
                self.collect_all = False

        elif self.phase == 3:
            pass

        elif self.phase == 4:
            if self.phase_timer >= 2000:
                self.in_pause = False
                self.phase = 0

    def next_wave(self):
        self.wave += 1
        self.enemies_killed = 0
        self.enemies_to_spawn = min(10 + self.wave * 10, 100)
        self.wave_complete = False

    def start_next_wave(self):
        if self.phase == 0:
            return
        self.next_wave()
        self.phase = 4
        self.phase_timer = 0
        self.in_pause = True

    def draw(self, screen):
        import pygame
        if self.phase == 4:
            font_big = pygame.font.SysFont(None, 120)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            text = font_big.render(f"Level {self.wave}", True, (255, 220, 0))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, rect)