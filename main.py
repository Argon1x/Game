import os
import pygame
import sys

os.environ["SDL_RENDER_SCALE_QUALITY"] = "1"
from settings import *
from states import GameState
from player import Player
from spawner import Spawner
from wave_manager import WaveManager
from upgrades import UpgradeScreen
from menu import Menu, create_buttons
from asset_paths import SAND_TEXTURE, SOUNDS
from assets_loader import load_image
from camera import Camera, draw_sprite_group, draw_tiled_world

pygame.init()
pygame.mixer.music.load(str(SOUNDS["music"]))
pygame.mixer.music.set_volume(0.2)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
pygame.display.set_caption("Desert Survivor")
clock = pygame.time.Clock()
_fullscreen = False


def toggle_fullscreen():
    global screen, _fullscreen
    _fullscreen = not _fullscreen
    flags = pygame.SCALED | (pygame.FULLSCREEN if _fullscreen else 0)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

_sand_texture = None

def _get_sand_texture() -> pygame.Surface | None:
    global _sand_texture
    if _sand_texture is None and SAND_TEXTURE.exists():
        tex = load_image(SAND_TEXTURE)
        if tex is not None:
            _sand_texture = pygame.transform.smoothscale(tex, (256, 256))
    return _sand_texture


def create_game():
    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    crystals_group = pygame.sprite.Group()
    spawner = Spawner()
    wave_manager = WaveManager()
    upgrade_screen = UpgradeScreen()
    return (
        player,
        player_group,
        enemies_group,
        bullets_group,
        crystals_group,
        spawner,
        wave_manager,
        upgrade_screen,
    )


class Game:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.running = True
        self.camera = Camera()
        self.reset_session()

        self.main_menu = Menu(
            "DESERT SURVIVOR",
            create_buttons([
                ("Играть", self.start_game),
                ("Выход", self.quit_game),
            ]),
        )
        self.pause_menu = Menu(
            "ПАУЗА",
            create_buttons([
                ("Продолжить", self.resume_game),
                ("В меню", self.go_to_main_menu),
                ("Выход", self.quit_game),
            ]),
        )
        self.game_over_menu = Menu(
            "GAME OVER",
            create_buttons([
                ("Заново", self.restart_game),
                ("В меню", self.go_to_main_menu),
            ]),
        )

    def reset_session(self):
        self.player = None
        self.player_group = None
        self.enemies_group = None
        self.bullets_group = None
        self.crystals_group = None
        self.spawner = None
        self.wave_manager = None
        self.upgrade_screen = None

    def start_game(self):
        pygame.mixer.music.play(-1)
        (
            self.player,
            self.player_group,
            self.enemies_group,
            self.bullets_group,
            self.crystals_group,
            self.spawner,
            self.wave_manager,
            self.upgrade_screen,
        ) = create_game()
        self.camera.follow(self.player.x, self.player.y)
        self.state = GameState.PLAYING

    def restart_game(self):
        self.start_game()

    def resume_game(self):
        self.state = GameState.PLAYING

    def pause_game(self):
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED

    def go_to_main_menu(self):
        pygame.mixer.music.stop()
        self.reset_session()
        self.state = GameState.MAIN_MENU

    def _gameplay_frozen(self) -> bool:
        if self.state == GameState.PAUSED:
            return True
        if self.upgrade_screen and self.upgrade_screen.visible:
            return True
        return False

    def trigger_game_over(self):
        pygame.mixer.music.stop()
        self.game_over_menu.set_subtitle(f"Счёт: {self.player.score}")
        self.state = GameState.GAME_OVER

    def quit_game(self):
        self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()
                return

            if self.state == GameState.MAIN_MENU:
                self.main_menu.handle_event(event)
            elif self.state == GameState.PAUSED:
                self.pause_menu.handle_event(event)
            elif self.state == GameState.GAME_OVER:
                self.game_over_menu.handle_event(event)
            elif self.state == GameState.PLAYING:
                self._handle_playing_event(event)

    def _handle_playing_event(self, event):
        if self.player is None or self.upgrade_screen is None:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self.upgrade_screen.visible:
                self.pause_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.upgrade_screen.handle_click(event.pos, self.player):
                if self.player.level_up_pending:
                    self.player.level_up_pending = False
                    self.upgrade_screen.show(self.player)
                else:
                    self.wave_manager.start_next_wave()

    def update(self, tick):
        if self.state != GameState.PLAYING:
            return

        self.wave_manager.update(tick)

        if self.wave_manager.phase == 3 and not self.upgrade_screen.visible:
            self.upgrade_screen.show(self.player)

        if self.player.level_up_pending and not self.upgrade_screen.visible:
            if self.wave_manager.phase == 0:
                self.player.level_up_pending = False
                self.upgrade_screen.show(self.player)

        if self._gameplay_frozen():
            self.player.handle_input(enabled=False)
        else:
            self.player.handle_input()

        self.player.update(tick)
        self.camera.follow(self.player.x, self.player.y)

        if self._gameplay_frozen():
            return

        self.spawner.update(self.enemies_group, self.wave_manager, self.player, tick)

        for enemy in self.enemies_group:
            enemy.update(self.player, tick)
            enemy.separate(self.enemies_group)
            enemy.check_collision_with_player(self.player)

        self.player.update_weapons(
            self.enemies_group,
            self.bullets_group,
            tick,
            self.crystals_group,
            self.wave_manager,
        )

        for bullet in self.bullets_group:
            bullet.update()
            for enemy in self.enemies_group:
                bullet.check_collision_with_enemy(
                    enemy, self.player, self.crystals_group, self.wave_manager
                )

        for crystal in self.crystals_group:
            crystal.update(self.player, self.wave_manager.collect_all, tick)

        if self.player.hp <= 0:
            self.trigger_game_over()

    def draw_game_world(self):
        if self.player is None:
            return

        sand = _get_sand_texture()
        draw_tiled_world(screen, sand, self.camera, fallback_color=SAND)

        draw_sprite_group(self.crystals_group, screen, self.camera)
        draw_sprite_group(self.enemies_group, screen, self.camera)
        draw_sprite_group(self.player_group, screen, self.camera)
        draw_sprite_group(self.bullets_group, screen, self.camera)

        for weapon in self.player.weapons:
            if hasattr(weapon, "draw"):
                weapon.draw(screen, self.player, self.camera)

        self.player.draw_ui(screen)
        self.wave_manager.draw(screen)
        self.upgrade_screen.draw(screen)

    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.main_menu.update()
            self.main_menu.draw(screen, dim_background=False, draw_desert_bg=True)
        elif self.state == GameState.PLAYING:
            self.draw_game_world()
        elif self.state == GameState.PAUSED:
            self.draw_game_world()
            self.pause_menu.update()
            self.pause_menu.draw(screen)
        elif self.state == GameState.GAME_OVER:
            self.draw_game_world()
            self.game_over_menu.update()
            self.game_over_menu.draw(screen)

    def run(self):
        try:
            while self.running:
                tick = clock.tick(FPS)
                self.handle_events()
                self.update(tick)
                self.draw()
                pygame.display.flip()
        except Exception:
            import traceback

            traceback.print_exc()
            pygame.quit()
            raise
        else:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    Game().run()
