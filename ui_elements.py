import pygame

from settings import YELLOW, SAND
from asset_paths import SOUNDS
from assets_loader import load_sound

_click_sound = None

def _get_click_sound():
    global _click_sound
    if _click_sound is None:
        _click_sound = load_sound(SOUNDS["click"], volume=0.3)
    return _click_sound

BTN_FILL = (72, 52, 34, 150)
BTN_HOVER = (105, 78, 48, 185)
BTN_SELECTED = (130, 96, 58, 210)
BTN_BORDER = (*SAND, 180)
BTN_BORDER_SELECTED = (*YELLOW, 230)
BTN_TEXT = (255, 242, 215)
BTN_TEXT_SELECTED = YELLOW


def _menu_font(size: int, *, bold: bool = False) -> pygame.font.Font:
    for name in ("arial", "helvetica", "segoeui", None):
        font = pygame.font.SysFont(name, size, bold=bold)
        if font is not None:
            return font
    return pygame.font.Font(None, size)


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback,
        color=BTN_FILL,
        hover_color=BTN_HOVER,
        selected_color=BTN_SELECTED,
        text_color=BTN_TEXT,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.selected_color = selected_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_selected = False
        self.font = _menu_font(38, bold=True)

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_selected:
            fill = self.selected_color
            border = BTN_BORDER_SELECTED
            text_color = BTN_TEXT_SELECTED
        elif self.is_hovered:
            fill = self.hover_color
            border = BTN_BORDER
            text_color = BTN_TEXT
        else:
            fill = self.color
            border = BTN_BORDER
            text_color = self.text_color

        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        inner = btn_surf.get_rect()
        pygame.draw.rect(btn_surf, fill, inner, border_radius=6)
        pygame.draw.line(
            btn_surf,
            (255, 230, 180, 45),
            (8, 3),
            (self.rect.width - 8, 3),
        )
        pygame.draw.rect(btn_surf, border, inner, 2, border_radius=6)

        if self.is_selected:
            marker = pygame.Rect(0, 10, 5, self.rect.height - 20)
            pygame.draw.rect(btn_surf, (*YELLOW, 230), marker, border_radius=2)

        surface.blit(btn_surf, self.rect.topleft)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(
            midleft=(self.rect.left + 22, self.rect.centery),
        )
        surface.blit(text_surf, text_rect)

    def handle_click(self, pos: tuple[int, int]) -> bool:
        if self.rect.collidepoint(pos):
            sound = _get_click_sound()
            if sound:
                sound.play()
            self.callback()
            return True
        return False

    def activate(self) -> None:
        sound = _get_click_sound()
        if sound:
            sound.play()
        self.callback()
