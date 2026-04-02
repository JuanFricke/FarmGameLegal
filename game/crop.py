from __future__ import annotations
from enum import Enum, auto
import pygame
from .constants import (
    TILE_SIZE, HUD_H,
    EMOJI_SEED, EMOJI_SPROUT, EMOJI_HARVEST,
    EMOJI_POTATO, EMOJI_CARROT, EMOJI_PUMPKIN, EMOJI_CORN,
)
from .tilemap import blit_emoji_centered


class CropType(Enum):
    POTATO  = auto()
    CARROT  = auto()
    PUMPKIN = auto()
    CORN    = auto()


CROP_EMOJI: dict[CropType, str] = {
    CropType.POTATO:  EMOJI_POTATO,
    CropType.CARROT:  EMOJI_CARROT,
    CropType.PUMPKIN: EMOJI_PUMPKIN,
    CropType.CORN:    EMOJI_CORN,
}


class GrowthStage(Enum):
    SEED    = 0   # just planted
    SPROUT  = 1   # code partially correct / first attempt
    MATURE  = 2   # code passed all tests
    HARVEST = 3   # harvested (brief sparkle)


# Frames each stage is shown for when animating growth (at 60 fps)
STAGE_DURATION = {
    GrowthStage.SEED:    0,    # stays until solved
    GrowthStage.SPROUT:  90,   # 1.5 s transition
    GrowthStage.MATURE:  0,    # stays until player harvests
    GrowthStage.HARVEST: 120,  # 2 s sparkle then tile cleared
}

# Scale factor per stage (fraction of TILE_SIZE)
STAGE_SCALE = {
    GrowthStage.SEED:    0.45,
    GrowthStage.SPROUT:  0.55,
    GrowthStage.MATURE:  0.72,
    GrowthStage.HARVEST: 0.72,
}


class Crop:
    def __init__(self, crop_type: CropType, tile) -> None:
        self.crop_type = crop_type
        self.tile = tile
        self.stage = GrowthStage.SEED
        self._frame = 0          # frames spent in current stage
        self._done = False       # True after HARVEST animation finishes

    # ------------------------------------------------------------------

    def advance_to_sprout(self) -> None:
        if self.stage == GrowthStage.SEED:
            self.stage = GrowthStage.SPROUT
            self._frame = 0

    def advance_to_mature(self) -> None:
        self.stage = GrowthStage.MATURE
        self._frame = 0

    def harvest(self) -> None:
        if self.stage == GrowthStage.MATURE:
            self.stage = GrowthStage.HARVEST
            self._frame = 0

    @property
    def is_done(self) -> bool:
        return self._done

    @property
    def is_harvestable(self) -> bool:
        return self.stage == GrowthStage.MATURE

    # ------------------------------------------------------------------

    def update(self) -> None:
        duration = STAGE_DURATION[self.stage]
        if duration > 0:
            self._frame += 1
            if self._frame >= duration:
                self._frame = 0
                if self.stage == GrowthStage.SPROUT:
                    pass   # stays sprout until code passes
                elif self.stage == GrowthStage.HARVEST:
                    self._done = True

    def _current_emoji(self) -> str:
        if self.stage == GrowthStage.SEED:
            return EMOJI_SEED
        if self.stage == GrowthStage.SPROUT:
            return EMOJI_SPROUT
        if self.stage == GrowthStage.MATURE:
            return CROP_EMOJI[self.crop_type]
        # HARVEST — alternate between crop and sparkle
        return EMOJI_HARVEST if (self._frame // 15) % 2 == 0 else CROP_EMOJI[self.crop_type]

    def draw(self, surface: pygame.Surface) -> None:
        cx = self.tile.col * TILE_SIZE + TILE_SIZE // 2
        cy = HUD_H + self.tile.row * TILE_SIZE + TILE_SIZE // 2
        scale = STAGE_SCALE[self.stage]
        size = int(TILE_SIZE * scale)

        # Slight bob for sprout stage
        if self.stage == GrowthStage.SPROUT:
            import math
            cy += int(3 * math.sin(self._frame * 0.15))

        blit_emoji_centered(surface, self._current_emoji(), cx, cy, size)
