import pygame
import sys
from settings import *
from player import Player
from enemies import Slime
from spawner import Spawner
from wave_manager import WaveManager
from upgrades import UpgradeScreen
from game_over import GameOver

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Desert Survivor")

clock = pygame.time.Clock()

def create_game():
    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies_group = pygame.sprite.Group()
    bullets_group = pygame.sprite.Group()
    crystals_group = pygame.sprite.Group()
    spawner = Spawner()
    wave_manager = WaveManager()
    upgrade_screen = UpgradeScreen()
    game_over = GameOver()
    return player, player_group, enemies_group, bullets_group, crystals_group, spawner, wave_manager, upgrade_screen, game_over

player, player_group, enemies_group, bullets_group, crystals_group, spawner, wave_manager, upgrade_screen, game_over = create_game()

running = True
while running:
    tick = clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over.visible:
                player, player_group, enemies_group, bullets_group, crystals_group, spawner, wave_manager, upgrade_screen, game_over = create_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if upgrade_screen.handle_click(event.pos, player):
                if player.level_up_pending:
                    player.level_up_pending = False
                    upgrade_screen.show(player)
                else:
                    wave_manager.start_next_wave()

    if not game_over.visible:
        wave_manager.update(tick)

        if wave_manager.phase == 3 and not upgrade_screen.visible:
            upgrade_screen.show(player)

        if player.level_up_pending and not upgrade_screen.visible:
            if wave_manager.phase == 0:
                player.level_up_pending = False
                upgrade_screen.show(player)

        player.handle_input()
        player.update(tick)

        if not upgrade_screen.visible:
            spawner.update(enemies_group, wave_manager)

            for enemy in enemies_group:
                enemy.update(player)
                enemy.separate(enemies_group)
                enemy.check_collision_with_player(player)

            player.update_weapons(enemies_group, bullets_group, tick, crystals_group, wave_manager)

            for b in bullets_group:
                b.update()
                for enemy in enemies_group:
                    b.check_collision_with_enemy(enemy, player, crystals_group, wave_manager)

            for crystal in crystals_group:
                crystal.update(player, wave_manager.collect_all)

            if player.hp <= 0:
                game_over.show()

    screen.fill(SAND)
    crystals_group.draw(screen)
    enemies_group.draw(screen)
    player_group.draw(screen)
    bullets_group.draw(screen)

    for weapon in player.weapons:
        if hasattr(weapon, 'draw'):
            weapon.draw(screen, player)

    player.draw_ui(screen)
    wave_manager.draw(screen)
    upgrade_screen.draw(screen)
    game_over.draw(screen, player)

    pygame.display.flip()

pygame.quit()
sys.exit()