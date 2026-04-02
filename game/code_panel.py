"""
Right-side status / results panel (read-only — no in-game editor).

States
------
IDLE        No tile selected — shows help text.
EDITING     External editor is open — shows "waiting" message.
RESULTS     Editor closed — shows per-test-case pass/fail table.
"""
from __future__ import annotations
from enum import Enum, auto
import pygame
from .constants import (
    SCREEN_W, SCREEN_H, HUD_H,
    FARM_W, CODE_PANEL_W,
    PANEL_BG, PANEL_BORDER,
    TEXT_COLOR, TEXT_DIM, HINT_COLOR, ERROR_COLOR, SUCCESS_COLOR,
)
from .sandbox import RunResult, CaseResult

_PAD        = 14
_LINE_H     = 19
_TITLE_SIZE = 15
_BODY_SIZE  = 13
_SMALL_SIZE = 12


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("monospace", size, bold=bold)


class PanelState(Enum):
    IDLE    = auto()
    EDITING = auto()
    RESULTS = auto()


class ResultsPanel:
    def __init__(self) -> None:
        self.state = PanelState.IDLE
        self.rect  = pygame.Rect(FARM_W, HUD_H, CODE_PANEL_W, SCREEN_H - HUD_H)

        # Data filled in by the game
        self.challenge_title: str        = ""
        self.challenge_desc: list[str]   = []
        self.function_name: str          = ""
        self.editor_name: str            = "nvim"
        self.all_editors: list[str]      = []
        self.plot_file: str              = ""
        self.result: RunResult | None    = None

        # Lazily created fonts
        self._tf: pygame.font.Font | None = None
        self._bf: pygame.font.Font | None = None
        self._sf: pygame.font.Font | None = None

    # ------------------------------------------------------------------
    # State transitions (called from main.py)
    # ------------------------------------------------------------------

    def show_idle(self) -> None:
        self.state = PanelState.IDLE
        self.result = None

    def show_editing(
        self,
        title: str,
        desc: list[str],
        function_name: str,
        editor: str,
        all_editors: list[str],
        path: str,
    ) -> None:
        self.state = PanelState.EDITING
        self.challenge_title = title
        self.challenge_desc  = desc
        self.function_name   = function_name
        self.editor_name     = editor
        self.all_editors     = all_editors
        self.plot_file       = path
        self.result          = None

    def show_results(self, result: RunResult, function_name: str = "") -> None:
        self.state  = PanelState.RESULTS
        self.result = result
        if function_name:
            self.function_name = function_name

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if self._tf is None:
            self._tf = _font(_TITLE_SIZE, bold=True)
            self._bf = _font(_BODY_SIZE)
            self._sf = _font(_SMALL_SIZE)

        pygame.draw.rect(surface, PANEL_BG, self.rect)
        pygame.draw.rect(surface, PANEL_BORDER, self.rect, 2)

        if self.state == PanelState.IDLE:
            self._draw_idle(surface)
        elif self.state == PanelState.EDITING:
            self._draw_editing(surface)
        elif self.state == PanelState.RESULTS:
            self._draw_results(surface)

    # ------------------------------------------------------------------
    # Internal draw helpers
    # ------------------------------------------------------------------

    def _x0(self) -> int:
        return self.rect.x + _PAD

    def _draw_line(
        self,
        surface: pygame.Surface,
        text: str,
        y: int,
        color: tuple,
        font: pygame.font.Font,
        max_w: int | None = None,
    ) -> int:
        """Blit one line, return new y. Clips text if it would overflow the panel."""
        avail = (max_w or (self.rect.right - _PAD)) - self._x0()
        # Truncate until it fits
        while text and font.size(text)[0] > avail:
            text = text[:-1]
        surf = font.render(text, True, color)
        surface.blit(surf, (self._x0(), y))
        return y + _LINE_H

    def _divider(self, surface: pygame.Surface, y: int) -> int:
        pygame.draw.line(
            surface, PANEL_BORDER,
            (self._x0(), y), (self.rect.right - _PAD, y),
        )
        return y + 8

    def _draw_editor_selector(self, surface: pygame.Surface, y: int) -> int:
        """Draw the editor picker row at the bottom of the panel."""
        footer_y = self.rect.bottom - _LINE_H * 3 - _PAD
        pygame.draw.line(surface, PANEL_BORDER,
                         (self._x0(), footer_y), (self.rect.right - _PAD, footer_y))
        footer_y += 6
        self._draw_line(surface, "ESPACO: mudar editor", footer_y, TEXT_DIM, self._sf)
        footer_y += _LINE_H

        # Editor list — highlight the active one
        x = self._x0()
        for name in self.all_editors:
            color = HINT_COLOR if name == self.editor_name else TEXT_DIM
            w = self._sf.size(name + "  ")[0]
            if x + w > self.rect.right - _PAD:
                break
            surf = self._sf.render(name, True, color)
            if name == self.editor_name:
                pygame.draw.rect(surface, PANEL_BORDER,
                                 (x - 2, footer_y - 1, surf.get_width() + 4, _LINE_H))
            surface.blit(surf, (x, footer_y))
            x += w
        return y

    def _draw_idle(self, surface: pygame.Surface) -> None:
        y = self.rect.y + _PAD
        y = self._draw_line(surface, "Farm Code", y, HINT_COLOR, self._tf)
        y = self._divider(surface, y + 4)

        for text, color in [
            ("Como jogar:", HINT_COLOR),
            ("", TEXT_DIM),
            ("WASD / Setas   Mover", TEXT_DIM),
            ("E              Interagir / Plantar", TEXT_DIM),
            ("               / Colher", TEXT_DIM),
            ("ESPACO         Mudar editor", TEXT_DIM),
            ("", TEXT_DIM),
            ("Aproxime-se de um canteiro", TEXT_DIM),
            ("e pressione E para plantar.", TEXT_DIM),
            ("O editor abre no terminal.", TEXT_DIM),
            ("", TEXT_DIM),
            ("Implemente a funcao pedida,", TEXT_DIM),
            ("salve e feche o editor.", TEXT_DIM),
            ("Os testes rodam automaticamente.", TEXT_DIM),
            ("", TEXT_DIM),
            ("Se passar, pressione E para", TEXT_DIM),
            ("colher a planta!", TEXT_DIM),
        ]:
            if text:
                y = self._draw_line(surface, text, y, color, self._bf)
            else:
                y += _LINE_H // 2

        self._draw_editor_selector(surface, y)

    def _draw_editing(self, surface: pygame.Surface) -> None:
        y = self.rect.y + _PAD
        y = self._draw_line(surface, self.challenge_title, y, HINT_COLOR, self._tf)
        y = self._divider(surface, y + 4)

        for line in self.challenge_desc:
            if line:
                y = self._draw_line(surface, line, y, TEXT_DIM, self._bf)
            else:
                y += _LINE_H // 2

        y = self._divider(surface, y + 8)

        y = self._draw_line(surface, f"Editando em: {self.editor_name}", y + 4, TEXT_COLOR, self._bf)
        y += _LINE_H // 2
        y = self._draw_line(surface, "Arquivo:", y, TEXT_DIM, self._sf)
        y = self._draw_line(surface, self.plot_file, y, HINT_COLOR, self._sf)
        y += _LINE_H
        y = self._draw_line(surface, "Salve e feche o editor para", y, TEXT_DIM, self._sf)
        y = self._draw_line(surface, "os testes rodarem.", y, TEXT_DIM, self._sf)

    def _draw_results(self, surface: pygame.Surface) -> None:
        r = self.result
        if r is None:
            return

        y = self.rect.y + _PAD

        # Header
        header = "Todos os testes passaram!" if r.passed else "Falhou em algum teste."
        hcol   = SUCCESS_COLOR if r.passed else ERROR_COLOR
        y = self._draw_line(surface, header, y, hcol, self._tf)

        if r.score:
            y = self._draw_line(surface, f"+{r.score} pontos", y, SUCCESS_COLOR, self._bf)

        if r.error and not r.cases:
            y = self._divider(surface, y + 4)
            for chunk in _wrap(r.error, 42):
                y = self._draw_line(surface, chunk, y, ERROR_COLOR, self._sf)
            y += 4

        y = self._divider(surface, y + 4)

        # Per-case table using the real function name
        fn = self.function_name
        bottom_reserved = _LINE_H * 4 + _PAD
        for case in r.cases:
            if y + _LINE_H > self.rect.bottom - bottom_reserved:
                y = self._draw_line(surface, "... (mais casos omitidos)", y, TEXT_DIM, self._sf)
                break
            label = case.label(fn)
            color = SUCCESS_COLOR if case.passed else ERROR_COLOR
            y = self._draw_line(surface, label, y, color, self._sf)

        # Footer controls
        footer_y = self.rect.bottom - _LINE_H * 3 - _PAD
        pygame.draw.line(surface, PANEL_BORDER,
                         (self._x0(), footer_y), (self.rect.right - _PAD, footer_y))
        footer_y += 6
        if r.passed:
            self._draw_line(surface, "E: colher   ESPACO: editor", footer_y, HINT_COLOR, self._sf)
        else:
            self._draw_line(surface, "E: editar   ESPACO: editor", footer_y, HINT_COLOR, self._sf)
        footer_y += _LINE_H
        # Editor list
        x = self._x0()
        for name in self.all_editors:
            color = HINT_COLOR if name == self.editor_name else TEXT_DIM
            surf = self._sf.render(name + "  ", True, color)
            if x + surf.get_width() > self.rect.right - _PAD:
                break
            if name == self.editor_name:
                pygame.draw.rect(surface, PANEL_BORDER,
                                 (x - 2, footer_y - 1, self._sf.size(name)[0] + 4, _LINE_H))
            surface.blit(self._sf.render(name, True, color), (x, footer_y))
            x += surf.get_width()


def _wrap(text: str, width: int) -> list[str]:
    """Very simple character-level wrap."""
    lines = []
    while len(text) > width:
        lines.append(text[:width])
        text = text[width:]
    if text:
        lines.append(text)
    return lines
