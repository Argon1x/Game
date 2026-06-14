import os
import shutil
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

from assets_loader import slice_stacked_sheet

SRC = Path("/Users/argonix/Downloads/processed_transparent_cropped_assets")
DST = Path(__file__).parent / "assets"

CROPPED = SRC / "cropped_png"
SLICED = SRC / "sliced_64_frames"
BACKGROUNDS = SRC / "kept_original_backgrounds"

COPY_FILES = [
    (CROPPED / "Slime corpse.png", "enemies/slime_sheet.png"),
    (CROPPED / "XP crystal.png", "pickups/xp_crystal.png"),
    (CROPPED / "Knife projectile.png", "projectiles/knife.png"),
    (CROPPED / "Orb projectile.png", "projectiles/orb.png"),
    (CROPPED / "Spike projectile.png", "projectiles/spike.png"),
    (CROPPED / "Boomerang projectile.png", "projectiles/boomerang.png"),
    (CROPPED / "Speed.png", "upgrades/speed_boost.png"),
    (CROPPED / "Damage.png", "upgrades/damage_boost.png"),
    (CROPPED / "Rapid Fire.png", "upgrades/rapid_fire.png"),
    (CROPPED / "Piercing.png", "upgrades/piercing.png"),
    (CROPPED / "Max Health.png", "upgrades/max_health.png"),
    (CROPPED / "Vampirism.png", "upgrades/vampirism.png"),
    (CROPPED / "Armor.png", "upgrades/armor.png"),
    (CROPPED / "Regeneration.png", "upgrades/regeneration.png"),
    (CROPPED / "Magnet.png", "upgrades/magnet.png"),
    (CROPPED / "XP Boost.png", "upgrades/xp_boost.png"),
    (CROPPED / "Knife_icon.png", "upgrades/knife.png"),
    (CROPPED / "Magic Orb_from_card.png", "upgrades/magic_orb.png"),
    (CROPPED / "Sand Spike_icon.png", "upgrades/sand_spike.png"),
    (CROPPED / "Boomerang_icon.png", "upgrades/boomerang.png"),
    (BACKGROUNDS / "Sand texture.png", "world/sand_texture.png"),
    (BACKGROUNDS / "menu.png", "ui/menu_background.png"),
]


def copy_tree(src_dir: Path, rel_dst: str) -> None:
    dst_dir = DST / rel_dst
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir)


def export_slime_frames(sheet_path: Path, rel_dst: str) -> None:
    if not sheet_path.exists():
        print("skip missing slime sheet")
        return

    dst_dir = DST / rel_dst
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)

    pygame.init()
    pygame.display.set_mode((1, 1))
    sheet = pygame.image.load(str(sheet_path)).convert_alpha()
    animations = slice_stacked_sheet(sheet)

    for direction, frames in animations.items():
        for index, frame in enumerate(frames, start=1):
            out = dst_dir / f"{direction}_{index}.png"
            pygame.image.save(frame, str(out))

    print("ok", rel_dst + "/", sum(len(v) for v in animations.values()), "frames")


def main() -> None:
    for src, rel in COPY_FILES:
        if not src.exists():
            print("skip missing", src.name)
            continue
        dst = DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print("ok", rel)

    bear_frames = SLICED / "bear_walk"
    if bear_frames.exists():
        copy_tree(bear_frames, "player/bear_walk")
        print("ok player/bear_walk/")

    slime_src = CROPPED / "Slime corpse.png"
    export_slime_frames(slime_src, "enemies/slime_walk")

    sliced_enemies = [
        ("worm_walk", "enemies/worm_walk"),
        ("bat_walk", "enemies/bat_walk"),
        ("bug_walk", "enemies/bug_walk"),
        ("Scorpion corpse", "enemies/scorpion_walk"),
    ]
    for src_name, rel_dst in sliced_enemies:
        src_dir = SLICED / src_name
        if src_dir.exists():
            copy_tree(src_dir, rel_dst)
            print("ok", rel_dst + "/")
        else:
            print("skip missing", src_name)


if __name__ == "__main__":
    main()
