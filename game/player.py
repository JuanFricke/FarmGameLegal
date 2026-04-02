from __future__ import annotations
import pygame
from .constants import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    HUD_H, EMOJI_PLAYER,
)
from .tilemap import Tilemap, Tile, blit_emoji_centered

MOVE_SPEED = 4          # pixels per frame
INTERACT_DIST = 1.5     # tiles — how close the player must be to interact


class Player:
    def __init__(self, tilemap: Tilemap) -> None:
        # Start in the middle of the map (pixel coords)
        self.x: float = (GRID_COLS // 2) * TILE_SIZE + TILE_SIZE / 2
        self.y: float = HUD_H + (GRID_ROWS // 2) * TILE_SIZE + TILE_SIZE / 2
        self.tilemap = tilemap

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def tile_col(self) -> int:
        return int(self.x // TILE_SIZE)

    @property
    def tile_row(self) -> int:
        return int((self.y - HUD_H) // TILE_SIZE)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def handle_movement(self, keys: pygame.key.ScancodeWrapper) -> None:
        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -MOVE_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = MOVE_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -MOVE_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = MOVE_SPEED

        new_x = self.x + dx
        new_y = self.y + dy

        half = TILE_SIZE * 0.45
        min_x = half
        max_x = GRID_COLS * TILE_SIZE - half
        min_y = HUD_H + half
        max_y = HUD_H + GRID_ROWS * TILE_SIZE - half

        self.x = max(min_x, min(max_x, new_x))
        self.y = max(min_y, min(max_y, new_y))

    def nearest_soil_tile(self) -> Tile | None:
        """Return the nearest tilled soil tile within interaction range."""
        best: Tile | None = None
        best_dist = float("inf")

        for dr in range(-2, 3):
            for dc in range(-2, 3):
                tile = self.tilemap.get_tile(self.tile_col + dc, self.tile_row + dr)
                if tile is None or tile.kind != "soil":
                    continue
                tx = tile.col * TILE_SIZE + TILE_SIZE / 2
                ty = HUD_H + tile.row * TILE_SIZE + TILE_SIZE / 2
                dist = ((self.x - tx) ** 2 + (self.y - ty) ** 2) ** 0.5 / TILE_SIZE
                if dist < INTERACT_DIST and dist < best_dist:
                    best_dist = dist
                    best = tile
        return best

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        blit_emoji_centered(surface, EMOJI_PLAYER, int(self.x), int(self.y), size=50)
