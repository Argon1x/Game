import pygame
from settings import *

class GameOver:
    def __init__(self):
        self.visible = False

    def show(self):
        self.visible = True

    def draw(self, screen, player):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        font_big   = pygame.font.SysFont(None, 120)
        font_med   = pygame.font.SysFont(None, 60)
        font_small = pygame.font.SysFont(None, 40)

        text = font_big.render("GAME OVER", True, (220, 50, 50))
        r = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(text, r)

        score_text = font_med.render(f"Score: {player.score}", True, (255, 220, 0))
        r2 = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(score_text, r2)

        hint = font_small.render("Press R to restart", True, (180, 180, 180))
        r3 = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(hint, r3)