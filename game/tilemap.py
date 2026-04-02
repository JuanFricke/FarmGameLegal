from __future__ import annotations
import functools
import pygame
from .constants import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    GRASS_COLOR, SOIL_COLOR, SOIL_TILLED,
    PANEL_BORDER, HIGHLIGHT_COLOR, HUD_H,
    NOTO_EMOJI_FONT,
)

# ---------------------------------------------------------------------------
# Emoji rendering helper
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=64)
def _get_emoji_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(NOTO_EMOJI_FONT, size)


_emoji_cache: dict[tuple[str, int], pygame.Surface] = {}


def render_emoji(emoji: str, size: int = 48) -> pygame.Surface:
    """Return a Surface with the emoji rendered at *size* px (cached)."""
    key = (emoji, size)
    if key not in _emoji_cache:
        font = _get_emoji_font(size)
        surf = font.render(emoji, True, (255, 255, 255))
        _emoji_cache[key] = surf
    return _emoji_cache[key]


def blit_emoji_centered(
    target: pygame.Surface,
    emoji: str,
    cx: int,
    cy: int,
    size: int = 48,
) -> None:
    """Blit *emoji* centred at pixel (cx, cy) on *target*."""
    surf = render_emoji(emoji, size)
    r = surf.get_rect(center=(cx, cy))
    target.blit(surf, r)


# ---------------------------------------------------------------------------
# Tile
# ---------------------------------------------------------------------------

class TileKind:
    GRASS = "grass"
    SOIL  = "soil"    # tilled, ready for a crop


class Tile:
    def __init__(self, col: int, row: int, kind: str = TileKind.GRASS) -> None:
        self.col = col
        self.row = row
        self.kind = kind
        self.crop = None          # set to a Crop instance when planted
        self.highlighted = False

    @property
    def rect(self) -> pygame.Rect:
        x = self.col * TILE_SIZE
        y = HUD_H + self.row * TILE_SIZE
        return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def is_plantable(self) -> bool:
        return self.kind == TileKind.SOIL and self.crop is None

    def draw(self, surface: pygame.Surface) -> None:
        r = self.rect

        if self.kind == TileKind.GRASS:
            color = GRASS_COLOR
        else:
            color = SOIL_TILLED

        pygame.draw.rect(surface, color, r)

        # subtle grid line
        pygame.draw.rect(surface, (0, 0, 0, 40), r, 1)

        if self.highlighted:
            hl = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            hl.fill((255, 220, 80, 60))
            surface.blit(hl, r.topleft)
            pygame.draw.rect(surface, HIGHLIGHT_COLOR, r, 2)


# ---------------------------------------------------------------------------
# Tilemap
# ---------------------------------------------------------------------------

class Tilemap:
    def __init__(self) -> None:
        self.tiles: list[list[Tile]] = [
            [Tile(c, r) for c in range(GRID_COLS)]
            for r in range(GRID_ROWS)
        ]
        self._init_soil_patches()

    def _init_soil_patches(self) -> None:
        """Pre-till several 2×2 soil patches where crops can be planted."""
        patches = [
            (1, 1), (1, 3), (1, 5),
            (4, 1), (4, 3), (4, 5),
            (7, 1), (7, 3), (7, 5),
        ]
        for base_col, base_row in patches:
            for dc in range(2):
                for dr in range(2):
                    c, r = base_col + dc, base_row + dr
                    if 0 <= c < GRID_COLS and 0 <= r < GRID_ROWS:
                        self.tiles[r][c].kind = TileKind.SOIL

    def get_tile(self, col: int, row: int) -> Tile | None:
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            return self.tiles[row][col]
        return None

    def tile_at_pixel(self, px: int, py: int) -> Tile | None:
        col = px // TILE_SIZE
        row = (py - HUD_H) // TILE_SIZE
        return self.get_tile(col, row)

    def clear_highlights(self) -> None:
        for row in self.tiles:
            for tile in row:
                tile.highlighted = False

    def draw(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.draw(surface)
