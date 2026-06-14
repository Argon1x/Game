import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH, WORLD_HEIGHT, WORLD_WIDTH


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def follow(self, target_x: float, target_y: float) -> None:
        self.x = target_x - SCREEN_WIDTH / 2
        self.y = target_y - SCREEN_HEIGHT / 2

        max_x = max(0, WORLD_WIDTH - SCREEN_WIDTH)
        max_y = max(0, WORLD_HEIGHT - SCREEN_HEIGHT)
        self.x = max(0.0, min(self.x, float(max_x)))
        self.y = max(0.0, min(self.y, float(max_y)))

    def apply(self, x: float, y: float) -> tuple[int, int]:
        return int(x - self.x), int(y - self.y)

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-int(self.x), -int(self.y))


def draw_sprite_group(group: pygame.sprite.Group, surface: pygame.Surface, camera: Camera) -> None:
    for sprite in group:
        surface.blit(sprite.image, camera.apply_rect(sprite.rect))


def draw_tiled_world(
    surface: pygame.Surface,
    texture: pygame.Surface,
    camera: Camera,
    *,
    fallback_color,
) -> None:
    if texture is None:
        surface.fill(fallback_color)
        return

    tw, th = texture.get_size()
    cam_x = int(camera.x)
    cam_y = int(camera.y)
    start_x = (cam_x // tw) * tw
    start_y = (cam_y // th) * th

    for wy in range(start_y, cam_y + SCREEN_HEIGHT + th, th):
        for wx in range(start_x, cam_x + SCREEN_WIDTH + tw, tw):
            surface.blit(texture, (wx - cam_x, wy - cam_y))
