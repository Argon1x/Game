from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"

SOUNDS_DIR = ASSETS_DIR / "sounds"

WORLD_DIR = ASSETS_DIR / "world"
UI_DIR = ASSETS_DIR / "ui"
PLAYER_DIR = ASSETS_DIR / "player"
ENEMIES_DIR = ASSETS_DIR / "enemies"
PICKUPS_DIR = ASSETS_DIR / "pickups"
PROJECTILES_DIR = ASSETS_DIR / "projectiles"
UPGRADES_DIR = ASSETS_DIR / "upgrades"

SAND_TEXTURE = WORLD_DIR / "sand_texture.png"
MENU_BACKGROUND = UI_DIR / "menu_background.png"

PLAYER_FRAMES_DIR = PLAYER_DIR / "bear_walk"
SLIME_FRAMES_DIR = ENEMIES_DIR / "slime_walk"
WORM_FRAMES_DIR = ENEMIES_DIR / "worm_walk"
BAT_FRAMES_DIR = ENEMIES_DIR / "bat_walk"
BUG_FRAMES_DIR = ENEMIES_DIR / "bug_walk"
SCORPION_FRAMES_DIR = ENEMIES_DIR / "scorpion_walk"
XP_CRYSTAL = PICKUPS_DIR / "xp_crystal.png"

PROJECTILE_SPRITES = {
    "knife": PROJECTILES_DIR / "knife.png",
    "orb": PROJECTILES_DIR / "orb.png",
    "spike": PROJECTILES_DIR / "spike.png",
    "boomerang": PROJECTILES_DIR / "boomerang.png",
}

SOUNDS = {
    "knife_shoot": SOUNDS_DIR / "knife_swoosh.wav",
    "enemy_hit":   SOUNDS_DIR / "enemy_hit.wav",
    "enemy_death": SOUNDS_DIR / "death_sound.wav",
    "pickup":      SOUNDS_DIR / "pick_up.ogg",
    "levelup":     SOUNDS_DIR / "levelup.wav",
    "player_hurt": SOUNDS_DIR / "get_hurt.wav",
    "music":       SOUNDS_DIR / "desert_wasteland.ogg",
    "click":       SOUNDS_DIR / "click.ogg",
}

UPGRADE_SPRITES = {
    "Speed Boost": UPGRADES_DIR / "speed_boost.png",
    "Damage Boost": UPGRADES_DIR / "damage_boost.png",
    "Rapid Fire": UPGRADES_DIR / "rapid_fire.png",
    "Piercing": UPGRADES_DIR / "piercing.png",
    "Max Health": UPGRADES_DIR / "max_health.png",
    "Vampirism": UPGRADES_DIR / "vampirism.png",
    "Armor": UPGRADES_DIR / "armor.png",
    "Regeneration": UPGRADES_DIR / "regeneration.png",
    "Magnet": UPGRADES_DIR / "magnet.png",
    "XP Boost": UPGRADES_DIR / "xp_boost.png",
    "Knife": UPGRADES_DIR / "knife.png",
    "Magic Orb": UPGRADES_DIR / "magic_orb.png",
    "Sand Spike": UPGRADES_DIR / "sand_spike.png",
    "Boomerang": UPGRADES_DIR / "boomerang.png",
}
