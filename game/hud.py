"""
HUD — top strip showing score, current phase, and interaction hints.
"""
from __future__ import annotations
import pygame
from .constants import (
    SCREEN_W, HUD_H,
    HUD_BG, TEXT_COLOR, TEXT_DIM, HINT_COLOR, SUCCESS_COLOR,
    FARM_W, CODE_PANEL_W,
)

_FONT_SIZE  = 15
_SMALL_SIZE = 12


class HUD:
    def __init__(self) -> None:
        self.score = 0
        self.phase_name = "Fase 1 - Batata"
        self.message = ""
        self.message_color: tuple = HINT_COLOR
        self._message_timer = 0   # frames left to show the message

        self._font: pygame.font.Font | None  = None
        self._sfont: pygame.font.Font | None = None

    # ------------------------------------------------------------------

    def add_score(self, points: int) -> None:
        self.score += points

    def set_phase(self, name: str) -> None:
        self.phase_name = name

    def flash(self, text: str, color: tuple = HINT_COLOR, duration_frames: int = 180) -> None:
        """Show a temporary message in the HUD for *duration_frames* frames."""
        self.message = text
        self.message_color = color
        self._message_timer = duration_frames

    def update(self) -> None:
        if self._message_timer > 0:
            self._message_timer -= 1
        else:
            self.message = ""

    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if self._font is None:
            self._font  = pygame.font.SysFont("monospace", _FONT_SIZE, bold=True)
            self._sfont = pygame.font.SysFont("monospace", _SMALL_SIZE)

        pygame.draw.rect(surface, HUD_BG, (0, 0, SCREEN_W, HUD_H))
        pygame.draw.line(surface, (60, 60, 80), (0, HUD_H - 1), (SCREEN_W, HUD_H - 1), 1)

        pad = 12
        cy = HUD_H // 2

        # Score
        score_surf = self._font.render(f"Pontos: {self.score}", True, SUCCESS_COLOR)
        surface.blit(score_surf, score_surf.get_rect(midleft=(pad, cy)))

        # Phase name (centred over farm area)
        phase_surf = self._font.render(self.phase_name, True, HINT_COLOR)
        surface.blit(phase_surf, phase_surf.get_rect(center=(FARM_W // 2, cy)))

        # Controls hint (far right of farm area)
        ctrl_surf = self._sfont.render("E: interagir   WASD: mover   ESC: sair", True, TEXT_DIM)
        surface.blit(ctrl_surf, ctrl_surf.get_rect(midright=(FARM_W - pad, cy)))

        # Flash message (shown below, centred on full width)
        if self.message and self._message_timer > 0:
            alpha = min(255, self._message_timer * 4)
            msg_surf = self._font.render(self.message, True, self.message_color)
            msg_surf.set_alpha(alpha)
            surface.blit(msg_surf, msg_surf.get_rect(center=(FARM_W // 2, cy + HUD_H - 4)))
