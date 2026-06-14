from pathlib import Path

import pygame

_cache: dict[tuple, pygame.Surface | None] = {}

DIRECTIONS = ("down", "left", "right", "up")


def load_image(path: Path, size: tuple[int, int] | None = None) -> pygame.Surface | None:
    if not path.exists():
        return None
    key = ("img", str(path), size)
    if key in _cache:
        return _cache[key]

    img = pygame.image.load(str(path)).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    _cache[key] = img
    return img


def load_sprite(path: Path, target_px: int) -> pygame.Surface | None:
    key = ("spr", str(path), target_px)
    if key in _cache:
        return _cache[key]

    img = load_image(path)
    if img is None:
        _cache[key] = None
        return None

    w, h = img.get_size()
    scale = target_px / max(w, h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    scaled = pygame.transform.smoothscale(img, (nw, nh))
    _cache[key] = scaled
    return scaled


def trim_frame(surface: pygame.Surface, alpha_threshold: int = 12) -> pygame.Surface:
    surface = surface.convert_alpha()
    w, h = surface.get_size()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            if surface.get_at((x, y))[3] > alpha_threshold:
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if not found:
        return surface
    rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return surface.subsurface(rect).copy()


def _row_has_pixel(surface: pygame.Surface, y: int) -> bool:
    w = surface.get_width()
    return any(surface.get_at((x, y))[3] > 20 for x in range(0, w, 2))


def _col_has_pixel(surface: pygame.Surface, x: int) -> bool:
    h = surface.get_height()
    return any(surface.get_at((x, y))[3] > 20 for y in range(0, h, 2))


def _find_horizontal_gaps(surface: pygame.Surface, min_gap: int = 10) -> list[tuple[int, int]]:
    w, h = surface.get_size()
    gaps: list[tuple[int, int]] = []
    gap_start = None
    for y in range(h):
        if not _row_has_pixel(surface, y):
            if gap_start is None:
                gap_start = y
        elif gap_start is not None and y - gap_start >= min_gap:
            gaps.append((gap_start, y))
            gap_start = None
        else:
            gap_start = None
    return gaps


def _find_vertical_gaps(surface: pygame.Surface, min_gap: int = 8) -> list[tuple[int, int]]:
    w, h = surface.get_size()
    gaps: list[tuple[int, int]] = []
    gap_start = None
    for x in range(w):
        if not _col_has_pixel(surface, x):
            if gap_start is None:
                gap_start = x
        elif gap_start is not None and x - gap_start >= min_gap:
            gaps.append((gap_start, x))
            gap_start = None
        else:
            gap_start = None
    return gaps


def _segments_from_gaps(length: int, gaps: list[tuple[int, int]], min_size: int = 30) -> list[tuple[int, int]]:
    segments: list[tuple[int, int]] = []
    start = 0
    for gap_start, gap_end in gaps:
        if gap_end - gap_start >= 8 and gap_start - start >= min_size:
            segments.append((start, gap_start))
            start = gap_end
    if length - start >= min_size:
        segments.append((start, length))
    return segments


def slice_stacked_sheet(surface: pygame.Surface) -> dict[str, list[pygame.Surface]]:
    w, h = surface.get_size()
    row_segments = _segments_from_gaps(h, _find_horizontal_gaps(surface))
    result: dict[str, list[pygame.Surface]] = {}

    for row_idx, direction in enumerate(DIRECTIONS):
        if row_idx >= len(row_segments):
            break
        y1, y2 = row_segments[row_idx]
        band = surface.subsurface((0, y1, w, y2 - y1))
        bw, bh = band.get_size()
        col_segments = _segments_from_gaps(bw, _find_vertical_gaps(band), min_size=20)
        frames: list[pygame.Surface] = []
        for x1, x2 in col_segments:
            cell = band.subsurface((x1, 0, x2 - x1, bh)).copy()
            frames.append(trim_frame(cell))
        if frames:
            result[direction] = frames

    return result


def load_directional_frames(frames_dir: Path, target_px: int) -> dict[str, list[pygame.Surface]]:
    key = ("frames", str(frames_dir), target_px)
    if key in _cache:
        return _cache[key]

    result: dict[str, list[pygame.Surface]] = {}
    for direction in DIRECTIONS:
        frames: list[pygame.Surface] = []
        index = 1
        while True:
            path = frames_dir / f"{direction}_{index}.png"
            if not path.exists():
                break
            frame = load_sprite(path, target_px)
            if frame is not None:
                frames.append(frame)
            index += 1
        if frames:
            result[direction] = frames

    if not result:
        fallback = pygame.Surface((target_px, target_px), pygame.SRCALPHA)
        result = {d: [fallback] for d in DIRECTIONS}

    _cache[key] = result
    return result
