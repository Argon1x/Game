from pathlib import Path

import pygame

from assets_loader import load_directional_frames

ANIM_TICKS_PER_FRAME = 10


class AnimatedCharacter:
    def __init__(
        self,
        frames_dir: Path,
        target_px: int,
        *,
        anim_ticks_per_frame: int = ANIM_TICKS_PER_FRAME,
    ):
        self.animations = load_directional_frames(frames_dir, target_px)
        self.anim_ticks_per_frame = anim_ticks_per_frame
        self.direction = "down"
        self.frame_index = 0
        self.anim_timer = 0
        self.moving = False
        self.image = self.animations["down"][0]

    def set_movement(self, dx: float, dy: float, *, moving: bool) -> None:
        self.moving = moving
        if not moving or (dx == 0 and dy == 0):
            return
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        elif dy < 0:
            self.direction = "up"
        else:
            self.direction = "down"

    def update(self, tick: int = 1) -> None:
        frames = self.animations[self.direction]
        if not self.moving:
            self.frame_index = 0
            self.anim_timer = 0
            self.image = frames[0]
            return

        self.anim_timer += tick
        if self.anim_timer >= self.anim_ticks_per_frame:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
