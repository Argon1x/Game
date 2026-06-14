import pygame
from collections.abc import Callable

from asset_paths import MENU_BACKGROUND
from assets_loader import load_image
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, YELLOW, WHITE, SAND, DARK_SAND
from ui_elements import Button, _menu_font

_menu_bg = None

MENU_MARGIN_X = 52
MENU_MARGIN_Y = 48
BUTTON_WIDTH = 280
BUTTON_HEIGHT = 52
BUTTON_GAP = 14


def _get_menu_background() -> pygame.Surface | None:
    global _menu_bg
    if _menu_bg is None and MENU_BACKGROUND.exists():
        bg = load_image(MENU_BACKGROUND)
        if bg is not None:
            _menu_bg = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    return _menu_bg


def create_buttons(items: list[tuple[str, Callable[[], None]]]) -> list[Button]:
    left_x = MENU_MARGIN_X
    bottom_y = SCREEN_HEIGHT - MENU_MARGIN_Y - BUTTON_HEIGHT

    buttons = []
    for index, (label, callback) in enumerate(items):
        y = bottom_y - (len(items) - 1 - index) * (BUTTON_HEIGHT + BUTTON_GAP)
        buttons.append(Button(left_x, y, BUTTON_WIDTH, BUTTON_HEIGHT, label, callback))
    return buttons


def _buttons_bounds(buttons: list[Button]) -> pygame.Rect:
    if not buttons:
        return pygame.Rect(MENU_MARGIN_X, SCREEN_HEIGHT - MENU_MARGIN_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

    top = min(button.rect.top for button in buttons)
    bottom = max(button.rect.bottom for button in buttons)
    return pygame.Rect(
        MENU_MARGIN_X - 20,
        top - 20,
        BUTTON_WIDTH + 40,
        bottom - top + 40,
    )


class Menu:
    def __init__(self, title: str, buttons: list[Button], subtitle: str | None = None):
        self.title = title
        self.buttons = buttons
        self.subtitle = subtitle
        self.selected_index = 0
        self.title_font = _menu_font(72, bold=True)
        self.subtitle_font = _menu_font(36)

    def set_subtitle(self, text: str | None) -> None:
        self.subtitle = text

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for index, button in enumerate(self.buttons):
            button.update(mouse_pos)
            if button.is_hovered:
                self.selected_index = index

        for index, button in enumerate(self.buttons):
            button.is_selected = index == self.selected_index

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.buttons:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.update()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.handle_click(event.pos):
                    return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.buttons[self.selected_index].activate()
                return True

        return False

    def _draw_title_block(self, surface: pygame.Surface) -> None:
        title_surf = self.title_font.render(self.title, True, YELLOW)
        title_pos = (MENU_MARGIN_X, 52)
        shadow = self.title_font.render(self.title, True, (20, 12, 6))
        surface.blit(shadow, (title_pos[0] + 2, title_pos[1] + 2))
        surface.blit(title_surf, title_pos)

        accent_y = 52 + title_surf.get_height() + 10
        pygame.draw.line(
            surface,
            DARK_SAND,
            (MENU_MARGIN_X, accent_y),
            (MENU_MARGIN_X + 220, accent_y),
            3,
        )
        pygame.draw.line(
            surface,
            (210, 180, 60),
            (MENU_MARGIN_X, accent_y + 4),
            (MENU_MARGIN_X + 120, accent_y + 4),
            2,
        )

        if self.subtitle:
            subtitle_surf = self.subtitle_font.render(self.subtitle, True, WHITE)
            surface.blit(subtitle_surf, (MENU_MARGIN_X, accent_y + 18))

    def _draw_button_panel(self, surface: pygame.Surface) -> None:
        panel_rect = _buttons_bounds(self.buttons)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (40, 28, 18, 90), panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, (*DARK_SAND, 110), panel.get_rect(), 2, border_radius=10)
        surface.blit(panel, panel_rect.topleft)

    def draw(
        self,
        surface: pygame.Surface,
        *,
        dim_background: bool = True,
        draw_desert_bg: bool = False,
    ) -> None:
        if draw_desert_bg:
            menu_bg = _get_menu_background()
            if menu_bg:
                surface.blit(menu_bg, (0, 0))
            else:
                surface.fill(SAND)
                for y in range(0, SCREEN_HEIGHT, 40):
                    pygame.draw.line(surface, DARK_SAND, (0, y), (SCREEN_WIDTH, y), 1)

            side_shade = pygame.Surface((420, SCREEN_HEIGHT), pygame.SRCALPHA)
            for x in range(420):
                alpha = int(130 * (1 - x / 420))
                pygame.draw.line(side_shade, (18, 10, 4, alpha), (x, 0), (x, SCREEN_HEIGHT))
            surface.blit(side_shade, (0, 0))
        elif dim_background:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((12, 8, 4, 165))
            surface.blit(overlay, (0, 0))
            side_shade = pygame.Surface((420, SCREEN_HEIGHT), pygame.SRCALPHA)
            for x in range(420):
                alpha = int(80 * (1 - x / 420))
                pygame.draw.line(side_shade, (0, 0, 0, alpha), (x, 0), (x, SCREEN_HEIGHT))
            surface.blit(side_shade, (0, 0))

        self._draw_title_block(surface)
        self._draw_button_panel(surface)

        for button in self.buttons:
            button.draw(surface)
